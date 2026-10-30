"""Stub Provider — 依存なしの決定的な生成器（テスト・配線確認用）。

本物のモデルは重い（torch・数十 GB のチェックポイント）ので、7 段フローの
配線・Resolve の出力・保存形式をモデル抜きで検証するために置く。
同じ seed・同じ Spec なら常に同じ波形を返す。
"""
from __future__ import annotations

import numpy as np

from semantic_audio_loom.types import ASSET_TYPES, Audio, GenerationRequest


class StubProvider:
    name = "stub"

    def capabilities(self) -> dict:
        return {
            "asset_types": list(ASSET_TYPES),
            "controls": ["prompt", "duration", "seed"],
            "languages": ["*"],
            "reproducibility": "seed",
        }

    def generate(self, request: GenerationRequest) -> Audio:
        spec = request.spec or {}
        duration = request.duration or spec.get("duration") or 1.0
        duration = float(min(max(float(duration), 0.1), 8.0))
        sample_rate = 32000 if request.asset_type == "bgm" else 44100
        n = int(round(duration * sample_rate))
        t = np.arange(n, dtype=np.float64) / sample_rate

        rng = np.random.default_rng(request.seed)
        base = 110.0 + (request.seed % 12) * 20.0
        wav = 0.20 * np.sin(2 * np.pi * base * t)
        wav += 0.10 * np.sin(2 * np.pi * base * 1.5 * t)
        wav += 0.02 * rng.standard_normal(n)

        fade = min(0.05, duration / 4.0)
        env = np.minimum(1.0, t / fade) * np.minimum(1.0, (duration - t) / fade)
        wav = (wav * np.clip(env, 0.0, 1.0)).astype(np.float32)

        if request.asset_type in ("bgm", "ambience"):
            wav = np.stack([wav, 0.9 * wav], axis=1).astype(np.float32)
        return Audio(wav=wav, sample_rate=sample_rate)
