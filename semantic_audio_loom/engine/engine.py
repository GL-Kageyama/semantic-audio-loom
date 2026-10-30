"""AudioAssetEngine — 7 段フロー（Validate → Route → Resolve → Generate →
Normalize → Tag → Store）をつなぐ。

asset_type で Resolve の出す Spec が変わる（voice=Performance / bgm=Music /
ambience・sfx・foley=Sound）。7 段の骨格は全 type で同じ。
seed 未指定ならここで採番し、params に記録する（regenerate で同じ結果を再現できる）。
"""
from __future__ import annotations

import random

from semantic_audio_loom import config
from semantic_audio_loom.engine import metadata, normalize, resolve, route, store, validate
from semantic_audio_loom.types import Audio, AudioAsset, GenerationIntent, GenerationRequest

# ループ資材は末尾フェードを掛けない（継ぎ目に無音ができる）。
_LOOPABLE = ("bgm", "ambience")


class AudioAssetEngine:
    def __init__(self, provider_name: str | None = None, resolve_mode: str = "llm", lang: str | None = None):
        self.provider_name = provider_name
        self.resolve_mode = resolve_mode
        self.lang = lang

    def generate(
        self,
        intent: GenerationIntent,
        out_dir: str | None = None,
        name: str | None = None,
    ) -> AudioAsset:
        # 1. seed 採番（未指定なら）
        seed = intent.seed if intent.seed is not None else random.randint(0, 2**31 - 1)

        # 1 Validate（人間の書く層）
        validate.validate_intent(intent)

        # 3 Resolve（Direction → Spec。asset_type で分岐）
        spec = resolve.resolve(intent, mode=self.resolve_mode, lang=self.lang)
        validate.validate_spec(spec, intent.asset_type)

        request = GenerationRequest(
            asset_type=intent.asset_type,
            spec=spec,
            seed=seed,
            quality=intent.quality,
            voice_profile=intent.voice_profile,
            dialogue=intent.dialogue,
            reading=intent.reading,
            duration=_requested_duration(intent, spec),
            provider_hint=self.provider_name,
        )
        return self._run(request, out_dir, name)

    def generate_request(
        self,
        request: GenerationRequest,
        out_dir: str | None = None,
        name: str | None = None,
    ) -> AudioAsset:
        """Resolve 済みの request から直接生成する（regenerate が保存済み Spec を
        再利用するため。LLM を再呼び出ししない＝再現性を保証）。"""
        validate.validate_spec(request.spec, request.asset_type)
        return self._run(request, out_dir, name)

    def _run(self, request: GenerationRequest, out_dir, name) -> AudioAsset:
        # 2 Route / 4 Generate / 5 Normalize
        provider = route.route(request.asset_type, request.provider_hint)
        audio = provider.generate(request)
        audio = self._normalize(request, audio)

        # 6 Tag / 7 Store
        meta = metadata.build(request, provider, audio)
        params = metadata.params(request, provider, audio)
        path = None
        if out_dir:
            path = store.save(audio, meta, params, out_dir, name)

        return AudioAsset(audio=audio, metadata=meta, parameters=params, path=path)

    def _normalize(self, request: GenerationRequest, audio: Audio) -> Audio:
        sample_rate, channels = config.OUTPUT_FORMATS[request.asset_type]
        loop = bool((request.spec.get("loop") or {}).get("enabled"))
        if request.asset_type == "voice":
            fade: float | None = normalize.TAIL_FADE_MS
        elif request.asset_type in _LOOPABLE and loop:
            fade = None
        else:
            fade = normalize.SFX_TAIL_FADE_MS
        return normalize.normalize(
            audio, sample_rate=sample_rate, channels=channels, tail_fade_ms=fade
        )


def _requested_duration(intent: GenerationIntent, spec: dict) -> float | None:
    value = (intent.sound or {}).get("duration", spec.get("duration"))
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None
