"""Tag（7 段フローの第 6 段）のうち、メタデータ構築。

metadata は「何を生成したか」（検索・参照用）。
parameters は「どう生成したか」（再現用。regenerate が読む）。
Resolve の結果（Spec）は parameters に完全写しして、regenerate が
LLM を再呼び出しせずに同じ Spec から再生成できるようにする（再現性の保証）。

metadata は asset_type を問わず平坦なキーで揃える（検索しやすさのため）。
"""
from __future__ import annotations

import datetime
import hashlib
import json

import numpy as np

from semantic_audio_loom import config
from semantic_audio_loom.types import Audio, GenerationRequest

_ROS_MAP = {"very_slow": 0.75, "slow": 0.9, "natural": 1.0, "fast": 1.12, "very_fast": 1.28}


def _channels(audio: Audio) -> int:
    return 1 if np.asarray(audio.wav).ndim == 1 else int(np.asarray(audio.wav).shape[1])


def _seconds(audio: Audio) -> float:
    arr = np.asarray(audio.wav)
    n = arr.shape[0] if arr.ndim else 0
    return round(n / float(audio.sample_rate), 3) if audio.sample_rate else 0.0


def _now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()


def build(request: GenerationRequest, provider, audio: Audio | None = None) -> dict:
    if request.asset_type == "voice":
        return _build_voice(request, provider)
    return _build_sound(request, provider, audio)


def _build_voice(request: GenerationRequest, provider) -> dict:
    voice = request.voice_profile.get("voice", {})
    spec = request.spec or {}
    emotion = spec.get("emotion") or {}
    prosody = spec.get("prosody") or {}
    return {
        "asset_type": "voice",
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
        "created_at": _now(),
    }


_SOUND_META_KEYS = (
    "role", "kind", "genre", "mood", "style", "instrumentation", "tempo",
    "key", "meter", "environment", "location", "time", "weather", "space",
    "distance", "density", "movement", "event", "object", "material",
    "action", "perspective", "surface", "contact", "intensity", "energy",
    "loop",
)


def _build_sound(request: GenerationRequest, provider, audio: Audio | None) -> dict:
    spec = request.spec or {}
    meta = {"asset_type": request.asset_type}
    for key in _SOUND_META_KEYS:
        value = spec.get(key)
        if value is not None:
            meta[key] = value
    meta["prompt"] = spec.get("prompt")
    if spec.get("subtext"):
        meta["subtext"] = spec["subtext"]
    meta["provider"] = provider.name
    if audio is not None:
        meta["sample_rate"] = audio.sample_rate
        meta["channels"] = _channels(audio)
        meta["duration"] = _seconds(audio)
    meta["created_at"] = _now()
    return meta


def params(request: GenerationRequest, provider, audio: Audio | None = None) -> dict:
    if request.asset_type == "voice":
        return _params_voice(request, provider)
    spec = request.spec or {}
    sample_rate = audio.sample_rate if audio else config.OUTPUT_FORMATS[request.asset_type][0]
    out = {
        "version": 3,
        "asset_type": request.asset_type,
        "provider": provider.name,
        "spec": spec,
        "seed": request.seed,
        "duration": request.duration,
        "sample_rate": sample_rate,
        "sha1": hashlib.sha1(
            json.dumps(spec, ensure_ascii=False, sort_keys=True).encode("utf-8")
        ).hexdigest()[:12],
    }
    # Spec にも seed にも入らないが音を変える設定（サンプリング回数など）。
    # 保存しないと params から同じ音を作れない。
    settings = getattr(provider, "runtime_settings", None)
    if callable(settings):
        out["provider_settings"] = settings()
    return out


def _params_voice(request: GenerationRequest, provider) -> dict:
    spec = request.spec or {}
    prosody = spec.get("prosody") or {}
    return {
        "version": 2,
        "provider": provider.name,
        "voice_profile": request.voice_profile,
        "performance_spec": spec,
        "dialogue": request.dialogue,
        "reading": request.reading,
        "seed": request.seed,
        "alpha": config.ALPHA,
        "beta": config.BETA,
        "rate_of_speech": _ROS_MAP.get(prosody.get("pace"), 1.0),
        "sha1": hashlib.sha1(request.dialogue.encode("utf-8")).hexdigest()[:12],
    }
