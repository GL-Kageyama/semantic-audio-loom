"""Validate（7 段フローの第 1 段）。

Resolve の前後で 2 つの検証を担う：

- `validate_intent(intent)` … 人間が書く層を検証。
    voice_profile → voice_profile.schema.json
    統合 Direction（emotion + volume/speed/pitch/breathiness/delivery）→
    performance_direction.schema.json
- `validate_spec(spec)` … Resolve の結果（AI が書く層）を検証。
    performance_spec.schema.json

Direction の intensity は「none/subtle/moderate/strong/overwhelming」（抽象レイヤ）。
Spec の intensity は実数 0.0〜1.0（Resolve が解決）。
"""
from __future__ import annotations

import json
import os

from semantic_audio_loom.types import GenerationIntent

_SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "schemas")


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


def validate_intent(intent: GenerationIntent) -> None:
    import jsonschema

    validate_voice_profile(intent.voice_profile)
    jsonschema.validate(_merged_direction(intent), _load("performance_direction.schema.json"))


def validate_spec(spec: dict) -> None:
    import jsonschema

    jsonschema.validate(spec, _load("performance_spec.schema.json"))


def validate_performance_asset(direction: dict) -> None:
    """演技の振り付け（performances/<name>.direction.yaml）を検証。

    Direction のフィールド（emotion/intensity/volume/speed/pitch/breathiness/
    pause_before/delivery）＋ situation/subtext。emotion のみ必須。
    """
    import jsonschema

    jsonschema.validate(direction, _load("performance_asset.schema.json"))
