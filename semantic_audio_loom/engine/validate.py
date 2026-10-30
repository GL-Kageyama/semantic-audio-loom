"""Validate（7 段フローの第 1 段）。

Resolve の前後で 2 つの検証を担う：

- `validate_intent(intent)` … 人間が書く層を検証。asset_type で分岐する。
    voice_profile → voice_profile.schema.json
    統合 Direction（emotion + volume/speed/pitch/breathiness/delivery）→
    performance_direction.schema.json
    bgm/ambience/sfx/foley の sound dict → 対応する Spec スキーマの「形」だけ
    （必須は Resolve が埋めるので課さない）
- `validate_spec(spec, asset_type)` … Resolve の結果（AI が書く層）を検証。
    voice=performance_spec / bgm=music_spec / ambience・sfx・foley=sound_spec

Direction の intensity は「none/subtle/moderate/strong/overwhelming」（抽象レイヤ）。
Spec の intensity は実数 0.0〜1.0（Resolve が解決）。
"""
from __future__ import annotations

import json
import os

from semantic_audio_loom.types import ASSET_TYPES, GenerationIntent, Scene

_SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "schemas")

# asset_type → Resolve 済み Spec のスキーマ。
SPEC_SCHEMAS = {
    "voice": "performance_spec.schema.json",
    "bgm": "music_spec.schema.json",
    "ambience": "sound_spec.schema.json",
    "sfx": "sound_spec.schema.json",
    "foley": "sound_spec.schema.json",
}


def _load(name: str) -> dict:
    with open(os.path.join(_SCHEMA_DIR, name), encoding="utf-8") as f:
        return json.load(f)


def _merged_direction(intent: GenerationIntent) -> dict:
    direction = {"emotion": intent.emotion.get("primary", "neutral")}
    intensity = intent.emotion.get("intensity")
    if intensity is not None:
        direction["intensity"] = intensity
    for key in ("volume", "speed", "pitch", "breathiness", "delivery"):
        value = intent.performance.get(key)
        if value is not None:
            direction[key] = value
    return direction


def validate_voice_profile(profile: dict) -> None:
    import jsonschema

    jsonschema.validate(profile, _load("voice_profile.schema.json"))


def _validate_sound_direction(intent: GenerationIntent) -> None:
    """sound dict の「形」を検証する（必須・kind 依存の条件は外す）。

    意味フィールドの不足は Resolve が situation から埋めるので、ここでは
    未知の enum 値・型の誤りだけを早く捕まえる。
    """
    import jsonschema

    sound = dict(intent.sound or {})
    if intent.asset_type != "bgm":
        sound.setdefault("kind", intent.asset_type)
    schema = _load(SPEC_SCHEMAS[intent.asset_type])
    relaxed = {k: v for k, v in schema.items() if k not in ("required", "allOf")}
    jsonschema.validate(sound, relaxed)


def validate_intent(intent: GenerationIntent) -> None:
    import jsonschema

    if intent.asset_type not in ASSET_TYPES:
        raise ValueError(
            f"unknown asset_type: {intent.asset_type!r} (expected one of {ASSET_TYPES})"
        )
    if intent.asset_type == "voice":
        validate_voice_profile(intent.voice_profile)
        jsonschema.validate(_merged_direction(intent), _load("performance_direction.schema.json"))
    else:
        _validate_sound_direction(intent)


def validate_spec(spec: dict, asset_type: str = "voice") -> None:
    import jsonschema

    if asset_type not in SPEC_SCHEMAS:
        raise ValueError(f"unknown asset_type: {asset_type!r} (expected one of {ASSET_TYPES})")
    jsonschema.validate(spec, _load(SPEC_SCHEMAS[asset_type]))


def validate_performance_asset(direction: dict) -> None:
    """演技の振り付け（performances/<name>.direction.yaml）を検証。

    Direction のフィールド（emotion/intensity/volume/speed/pitch/breathiness/
    pause_before/delivery）＋ situation/subtext。emotion のみ必須。
    """
    import jsonschema

    jsonschema.validate(direction, _load("performance_asset.schema.json"))


def validate_sound_bible(bible: dict) -> None:
    """作品の音響スタイル（sound-bible.yaml）を検証。"""
    import jsonschema

    jsonschema.validate(bible, _load("sound_bible.schema.json"))


def validate_library_asset(asset: dict) -> None:
    """ライブラリ資産のメタデータ（library/<type>/<name>.asset.yaml）を検証。"""
    import jsonschema

    jsonschema.validate(asset, _load("library_asset.schema.json"))


def _scene_to_dict(scene: Scene) -> dict:
    """Scene（dataclass）を scene.schema.json の形（flat Direction）へ変換する。"""
    cues = []
    for c in scene.cues:
        cue = {
            "character": c.character,
            "line": c.line,
            "emotion": c.emotion,
            "intensity": c.intensity,
            "situation": c.situation,
            "subtext": c.subtext,
            "pause_before": c.pause_before,
            "seed": c.seed,
            "name": c.name,
        }
        cue.update(c.performance)  # volume/speed/pitch/breathiness/delivery
        cues.append({k: v for k, v in cue.items() if v is not None})
    return {"name": scene.name, "default_pause": scene.default_pause, "cues": cues}


def validate_scene(scene: Scene) -> None:
    """scene（複数 voice キューの合成）を scene.schema.json で検証。"""
    import jsonschema

    jsonschema.validate(_scene_to_dict(scene), _load("scene.schema.json"))
