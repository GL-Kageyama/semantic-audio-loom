"""Tag（7 段フローの第 6 段）のうち、メタデータ構築。

metadata は「何を生成したか」（検索・参照用）。
parameters は「どう生成したか」（再現用。regenerate が読む）。
Resolve の結果（performance_spec）は parameters に完全写しして、regenerate が
LLM を再呼び出しせずに同じ Spec から再生成できるようにする（再現性の保証）。
"""
from __future__ import annotations

import datetime
import hashlib

from semantic_audio_loom import config
from semantic_audio_loom.types import GenerationRequest

_ROS_MAP = {"very_slow": 0.75, "slow": 0.9, "natural": 1.0, "fast": 1.12, "very_fast": 1.28}


def build(request: GenerationRequest, provider) -> dict:
    voice = request.voice_profile.get("voice", {})
    spec = request.performance_spec or {}
    emotion = spec.get("emotion") or {}
    prosody = spec.get("prosody") or {}
    return {
        "asset_type": request.asset_type,
        "character": request.voice_profile.get("character"),
        "age": voice.get("age"),
        "gender": voice.get("gender"),
        "emotion": emotion.get("primary"),
        "intensity": emotion.get("intensity"),
        "delivery": spec.get("delivery"),
        "intonation": prosody.get("intonation"),
        "subtext": spec.get("subtext"),
        "dialogue": request.dialogue,
        "provider": provider.name,
        "sample_rate": config.SAMPLE_RATE,
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


def params(request: GenerationRequest, provider) -> dict:
    spec = request.performance_spec or {}
    prosody = spec.get("prosody") or {}
    return {
        "version": 2,
        "provider": provider.name,
        "voice_profile": request.voice_profile,
        "performance_spec": spec,
        "dialogue": request.dialogue,
        "seed": request.seed,
        "alpha": config.ALPHA,
        "beta": config.BETA,
        "rate_of_speech": _ROS_MAP.get(prosody.get("pace"), 1.0),
        "sha1": hashlib.sha1(request.dialogue.encode("utf-8")).hexdigest()[:12],
    }
