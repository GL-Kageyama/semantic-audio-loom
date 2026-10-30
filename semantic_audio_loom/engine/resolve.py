"""Resolve（7 段フローの第 3 段）＝価値の核心。

Direction（監督＝意図）＋ State ＋ Scene ＋ Dialogue を、モデル非依存の
Spec（俳優＝実現）へ解決する。asset_type で 3 系統に分かれる：

- voice      → Performance Spec（`resolve.performance_spec.schema.json`）
- bgm        → Music Spec（`music_spec.schema.json`）
- ambience / sfx / foley → Sound Spec（`sound_spec.schema.json`）

voice の M0 で確定した Resolve の実体：
- subtext を「抽象文の追記」で渡しても音には乗らない（beta を上げても無効）。
- subtext を**具体的な抑揚指示（語尾の上げ下げ・ためらい・平坦）**へ変換して初めて乗る。
- よって LLM は subtext の推論だけでなく、それを Spec の prosody（特に
  `prosody.intonation`）へ具体化することを担う。

音の 3 系統では同じことが「モデル向けの英語プロンプト」への具体化にあたる。
LLM は構造フィールド（mood/style/environment/event/action…）と `prompt` を書く。

二実装：
- LLM  … 外部 LLM（Claude API）。既定。抽象語を具体的な音の記述へ落とす。
- Rule … 決定的な写像（LLM なし）。構造フィールドをそのまま Spec へ移し、
         プロンプトを決定的に組み立てる。

`resolve()` は mode で切り替え、LLM 失敗時は Rule へフォールバックして
パイプラインを止めない（崩れた Resolve で全体を落とさない）。
"""
from __future__ import annotations

import json
import sys

from semantic_audio_loom import i18n
from semantic_audio_loom.types import GenerationIntent

INTENSITY_MAP = {
    "none": 0.0, "subtle": 0.25, "moderate": 0.5, "strong": 0.75, "overwhelming": 1.0,
}
EFFORT_MAP = {
    "whisper": "relaxed", "quiet": "relaxed", "normal": "normal",
    "loud": "projected", "shout": "strained",
}

# Direction の sound dict から Spec へ持ち越すキー。
MUSIC_FIELDS = (
    "role", "genre", "mood", "style", "tempo", "key", "meter",
    "instrumentation", "arrangement", "texture", "energy", "duration",
    "loop", "references",
)
SOUND_FIELDS = (
    "kind", "mood", "style", "intensity", "duration", "loop",
    "environment", "location", "time", "weather", "space", "distance",
    "density", "movement", "event", "object", "material", "action",
    "perspective", "surface", "contact", "layers", "subtext",
)

_ROLE_TEXT = {
    "theme": "main theme",
    "underscore": "understated background score",
    "jingle": "short jingle",
    "loop": "seamless loop",
    "stinger": "short dramatic stinger",
}

_KIND_TEXT = {
    "ambience": "continuous ambience",
    "sfx": "single sound effect",
    "foley": "close-miked foley",
}


# ---------------------------------------------------------------- voice


def resolve_rule(intent: GenerationIntent) -> dict:
    """決定的な写像。Direction を Spec へ素直に移す（語尾 intonation は neutral）。"""
    emotion = intent.emotion or {}
    performance = intent.performance or {}
    primary = emotion.get("primary", "neutral")
    intensity_enum = emotion.get("intensity", "none")
    spec = {
        "emotion": {
            "primary": primary,
            "intensity": INTENSITY_MAP.get(intensity_enum, 0.5),
        },
        "loudness": {"effort": EFFORT_MAP.get(performance.get("volume", "normal"), "normal")},
        "prosody": {
            "pace": performance.get("speed", "natural"),
            "pitch": performance.get("pitch", "natural"),
            "intonation": "neutral",
            "pauses": [],
            "emphasis": [],
            "breath": [],
        },
        "subtext": intent.subtext or "",
    }
    if performance.get("delivery"):
        spec["delivery"] = performance["delivery"]
    return spec


def resolve_llm(intent: GenerationIntent, lang: str | None = None) -> dict:
    from semantic_audio_loom.llm.client import ClaudeClient

    prompts = i18n.load_prompts(lang)
    client = ClaudeClient()
    system = prompts["resolve"]["system"]
    user = _user_prompt(intent, prompts)
    return _strip_none(client.complete_json(system, user))


# ---------------------------------------------------------------- bgm


def resolve_music_rule(intent: GenerationIntent) -> dict:
    """bgm の決定的な写像。構造フィールドを Spec へ移し、プロンプトを組み立てる。"""
    sound = intent.sound or {}
    spec = {k: sound[k] for k in MUSIC_FIELDS if k in sound}
    prompt = sound.get("prompt")
    if not prompt:
        prompt = _music_prompt(spec)
        if intent.situation:
            prompt = f"{prompt}. Scene: {intent.situation}"
    spec["prompt"] = prompt
    negative = sound.get("negative") or []
    if negative:
        spec.setdefault("negative_prompt", ", ".join(negative))
    if intent.situation:
        spec.setdefault("subtext", intent.situation)
    return _strip_none(spec)


def resolve_music_llm(intent: GenerationIntent, lang: str | None = None) -> dict:
    from semantic_audio_loom.llm.client import ClaudeClient

    prompts = i18n.load_prompts(lang)
    client = ClaudeClient()
    system = prompts["resolve_music"]["system"]
    user = _sound_user_prompt(intent, prompts["resolve_music"], lang)
    return _strip_none(client.complete_json(system, user))


# ---------------------------------------------------------------- ambience / sfx / foley


def resolve_sound_rule(intent: GenerationIntent) -> dict:
    """ambience / sfx / foley の決定的な写像。kind だけは必ず入れる。"""
    sound = intent.sound or {}
    kind = intent.asset_type
    spec = {k: sound[k] for k in SOUND_FIELDS if k in sound}
    spec["kind"] = kind

    # kind 固有の必須フィールドを situation から埋める（無ければ汎用の既定）。
    fallback = intent.situation or sound.get("prompt") or ""
    if kind == "ambience":
        spec.setdefault("environment", fallback or "quiet steady ambience")
    elif kind == "sfx":
        spec.setdefault("event", fallback or "single impact")
    else:
        spec.setdefault("action", fallback or "cloth and footsteps")

    prompt = sound.get("prompt")
    if not prompt:
        prompt = _sound_prompt(spec, kind)
        if intent.situation:
            prompt = f"{prompt}. Scene: {intent.situation}"
    spec["prompt"] = prompt
    negative = sound.get("negative") or []
    if negative:
        spec.setdefault("negative_prompt", ", ".join(negative))
    return _strip_none(spec)


def resolve_sound_llm(intent: GenerationIntent, lang: str | None = None) -> dict:
    from semantic_audio_loom.llm.client import ClaudeClient

    prompts = i18n.load_prompts(lang)
    client = ClaudeClient()
    system = prompts["resolve_sound"]["system"]
    user = _sound_user_prompt(intent, prompts["resolve_sound"], lang)
    spec = _strip_none(client.complete_json(system, user))
    spec["kind"] = intent.asset_type  # LLM の言い値でなく asset_type を正とする
    return spec


# ---------------------------------------------------------------- dispatch


def resolve(intent: GenerationIntent, mode: str = "llm", lang: str | None = None) -> dict:
    asset_type = intent.asset_type
    if mode == "rule":
        return _rule(intent, asset_type)
    try:
        if asset_type == "voice":
            return resolve_llm(intent, lang=lang)
        if asset_type == "bgm":
            return resolve_music_llm(intent, lang=lang)
        return resolve_sound_llm(intent, lang=lang)
    except Exception as exc:  # 認証不可・ゲートウェイ障害・JSON 解釈失敗など
        print(
            i18n._t(
                i18n.load_locale(lang),
                "resolve",
                "fallback",
                "[resolve] LLM に失敗したため Rule へフォールバック: {exc}",
                exc=exc,
            ),
            file=sys.stderr,
        )
        return _rule(intent, asset_type)


def _rule(intent: GenerationIntent, asset_type: str) -> dict:
    if asset_type == "voice":
        return resolve_rule(intent)
    if asset_type == "bgm":
        return resolve_music_rule(intent)
    return resolve_sound_rule(intent)


# ---------------------------------------------------------------- prompt builders


def _strip_none(spec: dict) -> dict:
    """トップレベルの None 値を落とす（省略可能な enum フィールドを None で
    含めるとスキーマ検証に落ちるため。LLM が null を返しても通す）。"""
    return {k: v for k, v in spec.items() if v is not None}


def _music_prompt(spec: dict) -> str:
    """Music Spec の構造フィールドからモデル向けプロンプトを組み立てる。"""
    parts = []
    mood = spec.get("mood") or []
    if mood:
        parts.append(", ".join(str(x) for x in mood))
    style = spec.get("style") or spec.get("genre") or []
    if style:
        parts.append(", ".join(str(x) for x in style))
    instrumentation = spec.get("instrumentation") or []
    if instrumentation:
        parts.append("featuring " + ", ".join(str(x) for x in instrumentation))
    tempo = spec.get("tempo") or {}
    if tempo.get("bpm"):
        parts.append(f"{float(tempo['bpm']):.0f} BPM")
    elif tempo.get("feel"):
        parts.append(str(tempo["feel"]).replace("_", " ") + " tempo")
    key = spec.get("key") or {}
    key_text = " ".join(str(x) for x in (key.get("tonic"), key.get("mode")) if x)
    if key_text:
        parts.append(key_text)
    meter = spec.get("meter")
    if meter:
        parts.append(f"in {meter}")
    arrangement = spec.get("arrangement") or {}
    if arrangement.get("density"):
        parts.append(f"{arrangement['density']} arrangement")
    if arrangement.get("arc"):
        parts.append(str(arrangement["arc"]))
    texture = spec.get("texture") or []
    if texture:
        parts.append(", ".join(str(x) for x in texture))
    parts.append(_ROLE_TEXT.get(spec.get("role"), "instrumental music"))
    parts.append("instrumental, no vocals")
    prompt = ", ".join(p for p in parts if p)
    duration = spec.get("duration")
    if duration:
        prompt = f"{prompt}. About {_seconds_text(duration)}."
    return prompt


def _seconds_text(value) -> str:
    seconds = float(value)
    rounded = round(seconds) if seconds >= 10 else round(seconds, 1)
    unit = "second" if rounded == 1 else "seconds"
    return f"{rounded:g} {unit}"


def _sound_prompt(spec: dict, kind: str) -> str:
    """Sound Spec の構造フィールドからモデル向けプロンプトを組み立てる。"""
    parts = []
    if kind == "ambience":
        for key in ("environment", "location", "time", "weather"):
            if spec.get(key):
                parts.append(str(spec[key]))
        if spec.get("space"):
            parts.append(f"{spec['space']} space")
    elif kind == "sfx":
        for key in ("event", "object", "material"):
            if spec.get(key):
                parts.append(str(spec[key]))
        if spec.get("distance"):
            parts.append(f"{spec['distance']} perspective")
    else:
        for key in ("action", "object"):
            if spec.get(key):
                parts.append(str(spec[key]))
        if spec.get("surface"):
            parts.append(f"on {spec['surface']}")
        if spec.get("contact"):
            parts.append(str(spec["contact"]))

    for key in ("density", "movement", "intensity"):
        value = spec.get(key)
        if value is None:
            continue
        if key == "intensity":
            parts.append(f"intensity {float(value):.2f}")
        else:
            parts.append(f"{value} {key}")

    mood = spec.get("mood") or []
    if mood:
        parts.append(", ".join(str(x) for x in mood))
    style = spec.get("style") or []
    if style:
        parts.append(", ".join(str(x) for x in style))
    parts.append(_KIND_TEXT.get(kind, "sound"))

    prompt = ", ".join(p for p in parts if p)
    duration = spec.get("duration")
    if duration:
        prompt = f"{prompt}. About {_seconds_text(duration)}."
    return prompt


def _user_prompt(intent: GenerationIntent, prompts: dict) -> str:
    emotion = intent.emotion or {}
    performance = intent.performance or {}
    state = intent.character_state or {}
    scene = intent.scene or {}
    r = prompts["resolve"]
    none = r["none"]
    subtext_section = (
        r["subtext_given"].format(subtext=intent.subtext)
        if intent.subtext
        else r["subtext_infer"]
    )
    return r["user"].format(
        dialogue=intent.dialogue,
        situation=intent.situation or none,
        scene=json.dumps(scene, ensure_ascii=False) if scene else none,
        state=json.dumps(state, ensure_ascii=False) if state else none,
        emotion=emotion.get("primary", "neutral"),
        intensity=emotion.get("intensity", "none"),
        volume=performance.get("volume", "normal"),
        speed=performance.get("speed", "natural"),
        pitch=performance.get("pitch", "natural"),
        delivery=performance.get("delivery", "") or none,
        subtext_section=subtext_section,
    )


def _sound_user_prompt(intent: GenerationIntent, section: dict, lang: str | None = None) -> str:
    """bgm / ambience / sfx / foley の LLM 入力。"""
    none = i18n._t(
        i18n.load_locale(lang), "resolve", "none", "(指定なし)"
    )
    sound = intent.sound or {}
    scene = intent.scene or {}
    return section["user"].format(
        asset_type=intent.asset_type,
        situation=intent.situation or none,
        scene=json.dumps(scene, ensure_ascii=False) if scene else none,
        direction=json.dumps(sound, ensure_ascii=False, sort_keys=True) if sound else none,
        subtext=intent.subtext or none,
    )
