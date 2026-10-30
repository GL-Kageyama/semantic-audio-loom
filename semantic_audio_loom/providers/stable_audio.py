"""Stable Audio Open Provider（ambience / sfx / foley / 短い bgm）— ローカル生成。diffusers。

`stabilityai/stable-audio-open-1.0` は 44.1kHz stereo・最大約 47 秒。
モデルは gated（Hugging Face で利用許諾への同意＋`huggingface-cli login` が必要）。
Stability AI Community License に従う。

環境変数：
  SAL_STABLE_AUDIO_MODEL  既定 stabilityai/stable-audio-open-1.0
  SAL_DEVICE              既定 cpu（mps も指定できる）
"""
from __future__ import annotations

import os

import numpy as np

from semantic_audio_loom.types import Audio, GenerationRequest


class StableAudioProvider:
    name = "stable_audio"
    MODEL = os.environ.get("SAL_STABLE_AUDIO_MODEL", "stabilityai/stable-audio-open-1.0")
    SAMPLE_RATE = 44100
    MAX_SECONDS = 47.0

    def __init__(self):
        self._pipe = None
        self._torch = None

    def capabilities(self) -> dict:
        return {
            "asset_types": ["ambience", "sfx", "foley", "bgm"],
            "controls": ["prompt", "negative_prompt", "duration", "seed"],
            "languages": ["en"],
            "reproducibility": "seed",
            "max_seconds": self.MAX_SECONDS,
        }

    def _load(self):
        if self._pipe is not None:
            return self._torch, self._pipe
        try:
            import torch
            from diffusers import StableAudioPipeline
        except ImportError as exc:  # pragma: no cover - 環境依存
            raise RuntimeError(
                "stable_audio requires diffusers>=0.31 and torch: "
                "pip install 'diffusers>=0.31' torch"
            ) from exc

        try:
            pipe = StableAudioPipeline.from_pretrained(self.MODEL, torch_dtype=torch.float32)
        except Exception as exc:  # gated model / 未ログイン / 未同意
            raise RuntimeError(
                f"could not load {self.MODEL}. It is a gated model: accept the license on "
                "Hugging Face and run `huggingface-cli login`. "
                "Set SAL_STABLE_AUDIO_MODEL to use another checkpoint."
            ) from exc
        pipe = pipe.to(os.environ.get("SAL_DEVICE", "cpu"))
        self._pipe = pipe
        self._torch = torch
        return self._torch, self._pipe

    def generate(self, request: GenerationRequest) -> Audio:
        torch, pipe = self._load()
        spec = request.spec or {}
        prompt = spec.get("prompt") or ""
        duration = float(request.duration or spec.get("duration") or 4.0)
        duration = min(max(duration, 0.5), self.MAX_SECONDS)

        generator = torch.Generator("cpu").manual_seed(int(request.seed))
        result = pipe(
            prompt=prompt,
            negative_prompt=spec.get("negative_prompt") or "",
            num_inference_steps=100,
            audio_end_in_s=duration,
            width=512,
            height=512,
            num_waveforms_per_prompt=1,
            generator=generator,
        )
        wav = result.audios[0].detach().cpu().to(torch.float32).numpy()
        # diffusers は (channels, samples) を返す。保存・正規化の約束は (samples, channels)。
        wav = np.asarray(wav, dtype=np.float32)
        if wav.ndim == 2:
            wav = wav.T
        return Audio(wav=wav, sample_rate=self.SAMPLE_RATE)
