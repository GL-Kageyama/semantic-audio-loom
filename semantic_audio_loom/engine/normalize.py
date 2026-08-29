"""Normalize（7 段フローの第 5 段）。

声量三層分業の「Mixing（量）」レイヤの最小実装：

- 波形を float32 mono に正規化（downmix + NaN 除去）
- ピークを天井（既定 0.95）へ合わせる（クリップ回避）

「張り（loudness.effort）」はここでは触らない。あくまで再生音量の統一。
LUFS 基準のラウドネス正規化は M3 で（要 pyloudnorm）。
"""
from __future__ import annotations

import numpy as np

from semantic_audio_loom.types import Audio


def normalize(audio: Audio, ceiling: float = 0.95) -> Audio:
    wav = np.asarray(audio.wav, dtype=np.float32).squeeze()
    if wav.ndim != 1:
        wav = wav.mean(axis=0)
    wav = np.nan_to_num(wav, nan=0.0, posinf=0.0, neginf=0.0)
    peak = float(np.max(np.abs(wav))) if wav.size else 0.0
    if peak > 0.0:
        wav = wav * (ceiling / peak)
    return Audio(wav=wav, sample_rate=audio.sample_rate)
