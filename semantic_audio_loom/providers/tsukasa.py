"""Tsukasa_Speech Provider（M0 で確定）。

Tsukasa は自然言語の演技指示（KotoDama プロンプト）を 256 次元スタイルベクトル
（timbre 128 + prosody 128）へ変換し、参照音声と同じスロットで受ける。この Provider は
Direction（emotion/delivery/volume/speed）を KotoDama 散文へ変換し（translate）、
2 経路でスタイルを作る：

- 経路A（参照音声）: timbre を `compute_style_through_clip`、prosody をプロンプトから。
- 経路B（プロンプト）: timbre も prosody もプロンプトから（女性バイアスあり）。

モデルは重い（~5GB・import ~1 分）ので、初回 generate 時に遅延ロードしてプロセス内に保持する。
"""
from __future__ import annotations

import os
import random
import sys

import numpy as np

from semantic_audio_loom import config
from semantic_audio_loom.text import normalize_ellipsis
from semantic_audio_loom.types import Audio, GenerationRequest

_T = None
_phonemize = None

# Direction 語彙 → KotoDama 散文（英語。M0 実測で確定した言い回しを基本に）。
EMOTION_PHRASES = {
    "anxiety": "speaks quietly with a slight tremor, uneasy and hesitant",
    "sadness": "speaks low, soft and slow, pitch falling at the end, sighing and trailing off",
    "anger": "speaks sharp and clipped, each syllable punched with force, an edge of irritation",
    "fear": "speaks trembling and wavering, breathy and hesitant, quick and shallow",
    "joy": "speaks bright and warm, pitch rising, lively and light",
    "confidence": "speaks steady and firm, clear and assured",
    "loneliness": "speaks faint and distant, quiet and hollow",
    "excitement": "speaks fast and bright, energetic and upbeat",
    "calm": "speaks slowly and evenly, relaxed and smooth",
    "guilt": "speaks low and faltering, hesitant and downcast",
    "neutral": "speaks in a natural, even tone",
}

DELIVERY_PHRASES = {
    "restrained": "held back and controlled",
    "subtle": "understated and gentle",
    "suppressed": "bottled up, barely containing it",
    "controlled": "measured and precise",
    "flat": "flat and monotonous, no emphasis",
    "gentle": "soft and tender",
    "intimate": "close and quiet, nearly a whisper",
    "aggressive": "forceful and sharp, confrontational",
    "cheerful": "bright and upbeat",
    "cold": "cold and detached",
    "desperate": "urgent and pleading",
    "hesitant": "uncertain and faltering",
}

VOLUME_PHRASES = {
    "whisper": "barely above a whisper",
    "quiet": "quietly",
    "normal": "at a normal volume",
    "loud": "loudly, projecting the voice",
    "shout": "shouting, at full volume",
}

SPEED_PHRASES = {
    "very_slow": "very slowly, drawn out",
    "slow": "slowly",
    "natural": "at a natural pace",
    "fast": "quickly",
    "very_fast": "very fast, rushing",
}

PITCH_WORDS = {
    "very_low": "very low", "low": "low", "medium_low": "medium-low",
    "medium": "medium", "medium_high": "medium-high", "high": "high",
    "very_high": "very high",
}

# Direction の pitch（Spec では prosody.pitch）→ 散文。capabilities() が pitch を
# 名乗っているのに散文へ渡していなかった（同じ台詞の三通りが二通りに潰れる）。
PITCH_PHRASES = {
    "very_low": "with a very low pitch",
    "low": "with a low pitch",
    "medium_low": "with a fairly low pitch",
    "slightly_low": "with a slightly lower pitch",
    "medium": "",
    "natural": "",
    "slightly_high": "with a slightly higher pitch",
    "medium_high": "with a fairly high pitch",
    "high": "with a high pitch",
    "very_high": "with a very high pitch",
}

AGE_WORDS = {
    "child": "child", "adolescent": "teenage", "young_adult": "young adult",
    "adult": "adult", "middle_aged": "middle-aged", "elderly": "elderly",
}

_SPEED_TO_ROS = {
    "very_slow": 0.75, "slow": 0.9, "natural": 1.0, "fast": 1.12, "very_fast": 1.28,
}

# 語尾の抑揚（M0 実測で「具体的な抑揚指示」として音に乗ることを確認した核心ノブ）。
INTONATION_PHRASES = {
    "rising": "pitch rising at the end of the sentence",
    "falling": "pitch falling at the end, trailing off",
    "flat": "flat and even at the end, no rise or fall",
    "wavering": "voice wavering at the end, uncertain and hesitant",
    "neutral": "",
}

# Spec の loudness.effort（張り）→ プロンプトの声量文言。
EFFORT_TO_VOLUME = {
    "relaxed": "quietly", "normal": "at a normal volume",
    "projected": "loudly, projecting the voice", "strained": "shouting, at full volume",
}

# emotion.intensity（0〜1）→ プロンプトの強度文言。
# emotion の文言だけでは強度が渡らない（anger subtle と strong がバイト一致した）。
# 感情の名前は「どの感情か」しか言わず、「どれほどか」は別に書く必要がある。
_INTENSITY_PHRASES = (
    (0.40, "the feeling is faint, barely showing"),
    (0.70, ""),
    (0.90, "the feeling is strong, close to the surface"),
    (1.01, "the feeling is overwhelming, at its limit"),
)


def _intensity_phrase(value) -> str:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return ""
    for upper, phrase in _INTENSITY_PHRASES:
        if v <= upper:
            return phrase
    return _INTENSITY_PHRASES[-1][1]


def _load_model():
    """importable を遅延ロード（モデル読込は cwd=tsukasa が必要）。一度だけ。"""
    global _T, _phonemize
    if _T is not None:
        return
    tsukasa = config.TSUKASA_DIR
    if tsukasa not in sys.path:
        sys.path.insert(0, tsukasa)
    old = os.getcwd()
    os.chdir(tsukasa)
    try:
        import importable as T
    finally:
        os.chdir(old)
    from Utils.phonemize.cotlet_phon import phonemize
    _T = T
    _phonemize = phonemize


def _subject(vp: dict) -> str:
    """プロンプトの主語。gender 明示 > 参照音声ファイル名 > 中性的な代用。"""
    gender = (vp.get("voice") or {}).get("gender")
    if gender == "female":
        return "She"
    if gender == "male":
        return "He"
    ref = vp.get("reference_audio") or (vp.get("voice") or {}).get("reference_audio")
    if ref:
        base = os.path.basename(str(ref)).lower()
        if "female" in base:
            return "She"
        if "male" in base:
            return "He"
    return "The speaker"


def _voice_description(vp: dict) -> str:
    voice = vp.get("voice", {})
    age = AGE_WORDS.get(voice.get("age"), "adult")
    texture = voice.get("texture") or "neutral"
    pitch = PITCH_WORDS.get(voice.get("pitch"), "natural")
    gender = (voice.get("gender") or "person") + "'s"
    return f"A {age} {gender} voice, {texture}, {pitch} pitch. "


def _spec_prompt(subject: str, spec: dict) -> str:
    """Performance Spec → KotoDama 散文。Spec のうち Provider が反映できる
    controls（emotion / intensity / delivery / 声量 / 速度 / 語尾 intonation）だけを
    自然言語の演技指示へ変換する。emphasis / breath / pauses は構造化制御が
    共通欠落なので落とす（capabilities() 参照）。"""
    emotion = spec.get("emotion") or {}
    prosody = spec.get("prosody") or {}
    loudness = spec.get("loudness") or {}

    primary = emotion.get("primary") or "neutral"
    parts = [EMOTION_PHRASES.get(primary, EMOTION_PHRASES["neutral"])]

    intensity = _intensity_phrase(emotion.get("intensity"))
    if intensity:
        parts.append(intensity)

    d = spec.get("delivery")
    if d in DELIVERY_PHRASES:
        parts.append(DELIVERY_PHRASES[d])

    # 声量は Direction の値（whisper〜shout）を優先する。effort（張り）だけだと
    # 囁きと quiet が同じ "quietly" になる。Spec に volume が無いときだけ effort を使う。
    volume = loudness.get("volume")
    if volume in VOLUME_PHRASES:
        parts.append(VOLUME_PHRASES[volume])
    else:
        effort = loudness.get("effort")
        if effort in EFFORT_TO_VOLUME:
            parts.append(EFFORT_TO_VOLUME[effort])

    pitch = prosody.get("pitch")
    if PITCH_PHRASES.get(pitch):
        parts.append(PITCH_PHRASES[pitch])

    pace = prosody.get("pace")
    if pace in SPEED_PHRASES:
        parts.append(SPEED_PHRASES[pace])

    intonation = prosody.get("intonation")
    if intonation in INTONATION_PHRASES and INTONATION_PHRASES[intonation]:
        parts.append(INTONATION_PHRASES[intonation])

    return f"{subject} " + ", ".join(parts) + ". "


def _resolve_reference(ref: str) -> str:
    """参照音声の指定（パス or 話者キー）を実ファイルパスへ解決。"""
    if os.path.exists(ref):
        return ref
    for cand in (
        os.path.join(config.REFERENCE_LIB, ref + ".wav"),
        os.path.join(config.REFERENCE_LIB, "cloned", ref + "_clone.wav"),
    ):
        if os.path.exists(cand):
            return cand
    raise FileNotFoundError(f"reference audio not found: {ref}")


class TsukasaProvider:
    name = "tsukasa"

    def capabilities(self) -> dict:
        return {
            "asset_types": ["voice"],
            "models": ["Tsukasa_Speech"],
            "controls": ["emotion", "intensity", "speed", "volume", "pitch", "delivery", "intonation"],
            # emphasis / breath / pauses の構造化制御は共通欠落（M0 実測）。
            "voice_consistency": "reference",
            "languages": ["ja"],
            "reproducibility": "seed",
        }

    def generate(self, request: GenerationRequest) -> Audio:
        _load_model()
        import torch

        spec = request.performance_spec or {}
        prosody = spec.get("prosody") or {}
        dialogue = request.dialogue
        seed = request.seed
        ros = _SPEED_TO_ROS.get(prosody.get("pace"), 1.0)

        # 読み（ふりがな《》を置換した本文）があればそれを phonemize する。
        # 無ければ台詞（dialogue）をそのまま phonemize（従来どおり）。
        # 省略記号「…」は構造化ポーズ非対応の Tsukasa で「へぇ」様の有声に化けるため、
        # phonemize 前に除去・正規化する（台詞自体は変えない）。
        line = _phonemize(normalize_ellipsis(request.reading or dialogue))

        subject = _subject(request.voice_profile)
        perf_prompt = _spec_prompt(subject, spec)

        ref = (request.voice_profile.get("reference_audio")
               or (request.voice_profile.get("voice") or {}).get("reference_audio"))
        if ref:
            # 経路A: timbre は参照音声、prosody はプロンプト。
            ref_path = _resolve_reference(ref)
            with torch.no_grad():
                timbre = _T.compute_style_through_clip(ref_path)[:, :128]
                prosody_vec = _T.Kotodama_Prompter(_T.model, perf_prompt, _T.device)[:, 128:]
            ref_s = torch.cat([timbre, prosody_vec], dim=1)
        else:
            # 経路B: timbre も prosody もプロンプトから。
            full = _voice_description(request.voice_profile) + perf_prompt
            with torch.no_grad():
                ref_s = _T.Kotodama_Prompter(_T.model, full, _T.device)

        # 拡散ノイズ（torch.randn）由来の run 間分散を seed で決定論化。
        torch.manual_seed(seed)
        np.random.seed(seed)
        random.seed(seed)
        wav = _T.inference(line, ref_s=ref_s, alpha=config.ALPHA, beta=config.BETA, rate_of_speech=ros)
        wav = np.asarray(wav).squeeze().astype(np.float32)
        return Audio(wav=wav, sample_rate=config.SAMPLE_RATE)
