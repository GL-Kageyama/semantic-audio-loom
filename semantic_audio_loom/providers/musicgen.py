"""MusicGen Provider（bgm）— ローカル生成。transformers。

`facebook/musicgen-small` は 32kHz mono・最大 30 秒。モデルは初回 generate で
遅延ロードし、プロセス内で保持する。実測（M2 Pro・CPU・重み取得済み）：5 秒の BGM で
約 37 秒。

環境変数：
  SAL_MUSICGEN_MODEL  既定 facebook/musicgen-small（medium / large も指定可）
  SAL_DEVICE          既定 cpu（mps も指定できるが、この規模では cpu が安定）
"""
from __future__ import annotations

import os

import numpy as np

from semantic_audio_loom.types import Audio, GenerationRequest


class MusicGenProvider:
    name = "musicgen"
    MODEL = os.environ.get("SAL_MUSICGEN_MODEL", "facebook/musicgen-small")
    SAMPLE_RATE = 32000
    MAX_SECONDS = 30.0
    TOKENS_PER_SECOND = 50  # MusicGen の生成レート
    GUIDANCE = 3.0

    def __init__(self):
        self._model = None
        self._processor = None
        self._torch = None
        self.last_settings = None

    def capabilities(self) -> dict:
        return {
            "asset_types": ["bgm"],
            "controls": ["prompt", "duration", "seed", "negative_prompt"],
            "languages": ["en"],
            "reproducibility": "seed",
            "max_seconds": self.MAX_SECONDS,
        }

    def _load(self):
        if self._model is not None:
            return self._torch, self._processor, self._model
        try:
            import torch
            from transformers import AutoProcessor, MusicgenForConditionalGeneration
        except ImportError as exc:  # pragma: no cover - 環境依存
            raise RuntimeError(
                "musicgen requires transformers and torch: "
                "pip install 'transformers>=4.40' torch"
            ) from exc

        self._processor = AutoProcessor.from_pretrained(self.MODEL)
        self._model = MusicgenForConditionalGeneration.from_pretrained(self.MODEL)
        self._model.to(os.environ.get("SAL_DEVICE", "cpu"))
        self._model.eval()
        self._torch = torch
        return self._torch, self._processor, self._model

    def generate(self, request: GenerationRequest) -> Audio:
        torch, processor, model = self._load()
        spec = request.spec or {}
        prompt = spec.get("prompt") or ""
        duration = float(request.duration or spec.get("duration") or 8.0)
        duration = min(max(duration, 1.0), self.MAX_SECONDS)
        tokens = max(64, int(round(duration * self.TOKENS_PER_SECOND)))
        # 生成の尺は秒でなくトークン数で決まる。丸めを params に残さないと
        # 「同じ Spec から同じ長さ」が再現できない。
        self.last_settings = {"tokens": tokens, "guidance_scale": self.GUIDANCE}

        inputs = processor(text=[prompt], padding=True, return_tensors="pt").to(model.device)
        torch.manual_seed(int(request.seed))
        with torch.no_grad():
            generated = model.generate(
                **inputs,
                do_sample=True,
                guidance_scale=self.GUIDANCE,
                max_new_tokens=tokens,
            )
        wav = generated[0, 0].detach().cpu().to(torch.float32).numpy()
        return Audio(wav=np.asarray(wav, dtype=np.float32), sample_rate=self.SAMPLE_RATE)

    def runtime_settings(self) -> dict:
        return dict(self.last_settings or {})
