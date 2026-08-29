"""AudioAssetEngine — 7 段フロー（Validate → Route → Resolve → Generate →
Normalize → Tag → Store）をつなぐ。

M2 で Resolve を追加：GenerationIntent（Direction）→ Performance Spec → Provider。
seed 未指定ならここで採番し、params に記録する（regenerate で同じ結果を再現できる）。
"""
from __future__ import annotations

import random

from semantic_audio_loom.engine import metadata, normalize, resolve, route, store, validate
from semantic_audio_loom.types import AudioAsset, GenerationIntent, GenerationRequest


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

        # 3 Resolve（Direction → Performance Spec）
        spec = resolve.resolve(intent, mode=self.resolve_mode, lang=self.lang)
        validate.validate_spec(spec)

        request = GenerationRequest(
            asset_type=intent.asset_type,
            voice_profile=intent.voice_profile,
            performance_spec=spec,
            dialogue=intent.dialogue,
            seed=seed,
            quality=intent.quality,
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
        validate.validate_spec(request.performance_spec)
        return self._run(request, out_dir, name)

    def _run(self, request: GenerationRequest, out_dir, name) -> AudioAsset:
        # 2 Route / 4 Generate / 5 Normalize
        provider = route.route(request.provider_hint)
        audio = provider.generate(request)
        audio = normalize.normalize(audio)

        # 6 Tag / 7 Store
        meta = metadata.build(request, provider)
        params = metadata.params(request, provider)
        path = None
        if out_dir:
            path = store.save(audio, meta, params, out_dir, name)

        return AudioAsset(audio=audio, metadata=meta, parameters=params, path=path)
