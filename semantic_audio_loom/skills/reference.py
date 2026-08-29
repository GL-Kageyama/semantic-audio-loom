"""reference Skill（参照音声ライブラリの拡充と解決を担う糊）。

参照音声（経路A の timbre 複製元）はライブラリ（config.REFERENCE_LIB）に .wav と
manifest.json（出典・ライセンス記録）で管理する。足りない声は bin/reference.py で拡充：
- synthesize: ローカル生成（Tsukasa 経路B・参照不要）で作る
- add: 著作権フリー音源（VCTK CC BY 4.0 / Common Voice CC0 など）の .wav を登録する

出典・ライセンスを manifest.json に必ず記録する（配布時に帰属表示が必要な音源があるため）。
"""
from __future__ import annotations

import json
import os

from semantic_audio_loom import config


def manifest_path() -> str:
    return os.path.join(config.REFERENCE_LIB, "manifest.json")


def load_manifest() -> dict:
    p = manifest_path()
    if not os.path.exists(p):
        return {}
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save_manifest(m: dict) -> None:
    os.makedirs(config.REFERENCE_LIB, exist_ok=True)
    with open(manifest_path(), "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=2)


def resolve_reference(ref: str) -> str | None:
    """参照音声の指定（パス or 話者キー）を実ファイルパスへ解決。見つからなければ None。

    Provider（tsukasa）の _resolve_reference と同じ解決規則。見つからない場合に
    generate.py が拡充（bin/reference.py）を案内するために使う。
    """
    if os.path.exists(ref):
        return ref
    for cand in (
        os.path.join(config.REFERENCE_LIB, ref + ".wav"),
        os.path.join(config.REFERENCE_LIB, "cloned", ref + "_clone.wav"),
    ):
        if os.path.exists(cand):
            return cand
    return None


def list_keys() -> list[str]:
    """登録済みの参照音声キー（実ファイルが存在するもの）を返す。"""
    m = load_manifest()
    return sorted(k for k in m if resolve_reference(k))


def register(key: str, wav_path: str, entry: dict) -> str:
    """ライブラリに .wav を <key>.wav として保存し、manifest.json に出典を記録する。

    entry は {age, gender, source, license, ...}（manifest.json と同じ形）。
    """
    import shutil

    os.makedirs(config.REFERENCE_LIB, exist_ok=True)
    dst = os.path.join(config.REFERENCE_LIB, key + ".wav")
    shutil.copyfile(wav_path, dst)
    m = load_manifest()
    m[key] = entry
    save_manifest(m)
    return dst


def duration_sec(path: str):
    """.wav の長さ（秒）を返す。読めなければ None。"""
    try:
        import soundfile as sf
        return round(float(sf.info(path).duration), 2)
    except Exception:
        try:
            import wave
            with wave.open(path, "rb") as w:
                return round(w.getnframes() / w.getframerate(), 2)
        except Exception:
            return None


def synthesize_reference(key: str, voice: dict, line: str | None = None, seed: int | None = None, provider: str | None = None) -> str:
    """キャラの声質（voice dict）から、経路B（参照不要）で参照音声を生成・登録する。

    voice は voice_profile の voice 部分（age/gender/pitch/texture/breathiness/resonance）。
    bin/reference.py（Step 0）と bin/distill.py（蒸留の --synthesize）が共用する。
    経路B は女性バイアスが強い（男性の深い声・老人は弱い）。

    戻り値は登録された .wav のパス。
    """
    from semantic_audio_loom.engine import AudioAssetEngine
    from semantic_audio_loom.types import GenerationIntent

    if not voice:
        raise ValueError("声の属性（voice）が空です")
    profile = {"character": key, "voice": dict(voice)}
    line = line or "こんにちは。今日は、穏やかな一日ですね。"
    intent = GenerationIntent(
        asset_type="voice",
        voice_profile=profile,
        emotion={"primary": "neutral", "intensity": "none"},
        performance={"delivery": "controlled", "speed": "natural"},
        dialogue=line,
        seed=seed,
    )

    engine = AudioAssetEngine(provider_name=provider, resolve_mode="rule")
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        asset = engine.generate(intent, out_dir=tmp, name=key)
        gender_code = {"female": "F", "male": "M"}.get(voice.get("gender"), "?")
        entry = {
            "age": voice.get("age", "adult"),
            "gender": gender_code,
            "duration_sec": duration_sec(asset.path),
            "source": "local generation (Tsukasa_Speech 経路B / Semantic Audio Loom synthesize)",
            "license": "generated — no upstream license",
            "source_files": [f"synthesized from profile: {voice}"],
        }
        dst = register(key, asset.path, entry)
    return dst
