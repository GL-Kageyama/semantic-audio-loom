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


class _GaussianNoiseSampler:
    """スケジューラの `BrownianTreeNoiseSampler` の代わり。

    `CosineDPMSolverMultistepScheduler` は SDE の枝しか持たず、区間の増分を
    torchsde の BrownianTree から取る。この組み合わせ（diffusers 0.31 + torchsde
    0.2.6 + Python 3.12）では木の構築が `RecursionError` で落ちる——木が要るのは
    区間を跨いで問い直すときで、前へ進む掃引では重ならない区間の増分が独立な
    正規で足りる。形と dtype は呼び手（スケジューラ）が渡す `x` から取る。

    返すのは**単位分散**の正規。縮尺（`sigma_t * sqrt(1 - exp(-2h))`）は
    スケジューラが掛けるので、ここで区間の幅を掛けると σ の大きい帯で
    桁違いのノイズが乗り、出力がプロンプトでなくヒスになる（実測）。
    """

    def __init__(self, x, sigma_min=None, sigma_max=None, seed=None):
        import torch

        self.shape = tuple(x.shape)
        self.dtype = x.dtype
        self.generator = torch.Generator("cpu")
        self.generator.manual_seed(0 if seed is None else int(seed) % (2**63))

    def __call__(self, t0, t1):
        import torch

        return torch.randn(self.shape, generator=self.generator, dtype=self.dtype)


_NOISE_PATCHED = False


def _install_noise_sampler_fallback() -> None:
    """スケジューラが木を建てる前に、増分の源を差し替える（プロセスに一度）。

    `self.noise_sampler is None` の枝で建てられるので、名前を差し替えるだけで
    torchsde が経路から外れる。別のスケジューラを使うチェックポイントでは
    この名前が引かれない——そのときは何も変わらない。
    """
    global _NOISE_PATCHED
    if _NOISE_PATCHED:
        return
    try:
        import diffusers.schedulers.scheduling_cosine_dpmsolver_multistep as cosine
    except ImportError:  # pragma: no cover - diffusers 無し
        return
    if hasattr(cosine, "BrownianTreeNoiseSampler"):
        cosine.BrownianTreeNoiseSampler = _GaussianNoiseSampler
        _NOISE_PATCHED = True


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
            # モデル側の言い分（403 か、ログインが無いのか）を捨てない。捨てると
            # 「同意したはずなのに」のときに、何をすればいいか分からなくなる。
            raise RuntimeError(
                f"could not load {self.MODEL}: {exc}. "
                "It is a gated model: log in with `huggingface-cli login` and press "
                "'Agree and access repository' on the model page (an account that has "
                "only logged in is not enough). Set SAL_STABLE_AUDIO_MODEL to use "
                "another checkpoint."
            ) from exc
        pipe = pipe.to(os.environ.get("SAL_DEVICE", "cpu"))
        _install_noise_sampler_fallback()
        self._pipe = pipe
        self._torch = torch
        return self._torch, self._pipe

    def generate(self, request: GenerationRequest) -> Audio:
        torch, pipe = self._load()
        spec = request.spec or {}
        prompt = spec.get("prompt") or ""
        duration = float(request.duration or spec.get("duration") or 4.0)
        duration = min(max(duration, 0.5), self.MAX_SECONDS)
        steps = int(os.environ.get("SAL_STABLE_AUDIO_STEPS", "100"))
        self.last_steps = steps

        generator = torch.Generator("cpu").manual_seed(int(request.seed))
        # 増分の源はスケジューラに挟まって残る。捨てないと同じ seed でも
        # 2 回目から別の音になる（seed 決定論の破れ）。
        pipe.scheduler.noise_sampler = None
        # StableAudioPipeline は width/height を取らない（それは AudioLDM の口）。
        # 尺は audio_end_in_s だけ。ここを間違えると実モデルでは必ず TypeError になり、
        # stub だけで通した経路が「動いている」ように見える。
        result = pipe(
            prompt=prompt,
            negative_prompt=spec.get("negative_prompt") or "",
            num_inference_steps=steps,
            guidance_scale=float(spec.get("guidance_scale") or 7.0),
            audio_end_in_s=duration,
            num_waveforms_per_prompt=1,
            generator=generator,
        )
        wav = result.audios[0].detach().cpu().to(torch.float32).numpy()
        # diffusers は (channels, samples) を返す。保存・正規化の約束は (samples, channels)。
        wav = np.asarray(wav, dtype=np.float32)
        if wav.ndim == 2:
            wav = wav.T
        return Audio(wav=wav, sample_rate=self.SAMPLE_RATE)

    def runtime_settings(self) -> dict:
        """音を変える設定で、Spec にも seed にも入らないもの。

        `num_inference_steps` を変えると波形が変わるので、保存しないと
        「同じ params から同じ音」が崩れる（seed 決定論の前提）。
        """
        return {"steps": getattr(self, "last_steps", int(os.environ.get("SAL_STABLE_AUDIO_STEPS", "100")))}
