"""Store（7 段フローの第 7 段）。

WAV（16bit PCM mono）と params（YAML）を out_dir に保存し、WAV のパスを返す。
params は generate が決定した全入力（voice_profile の複写を含む）を持ち、
regenerate が単独で再現できるよう自己完結にする。
"""
from __future__ import annotations

import os
import wave

import numpy as np
import yaml

from semantic_audio_loom.types import Audio


def save(audio: Audio, metadata: dict, parameters: dict, out_dir: str, name: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    base = name or "asset"

    wav_path = os.path.join(out_dir, base + ".wav")
    wav = np.asarray(audio.wav, dtype=np.float32).squeeze()
    pcm16 = (np.clip(wav, -1.0, 1.0) * 32767.0).astype(np.int16)
    with wave.open(wav_path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(audio.sample_rate)
        w.writeframes(pcm16.tobytes())

    params_path = os.path.join(out_dir, base + ".params.yaml")
    with open(params_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(
            {"name": base, "metadata": metadata, "parameters": parameters},
            f, allow_unicode=True, sort_keys=False,
        )

    return wav_path
