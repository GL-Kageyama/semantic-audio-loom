#!/usr/bin/env python
"""ducking が実際に何 dB 沈めているかを測る（申告ではなく実測）。

mix.yaml の bed と voice を別々に重ね、mix.duck を通してから
「声が鳴っている区間」と「鳴っていない区間」の bed の RMS を比べる。

  PYTHONPATH=. <venv> .../check_duck.py projects/longform/drama/mix.yaml
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, REPO)

from semantic_audio_loom.engine import mix  # noqa: E402
from semantic_audio_loom.skills.probe import read_wav  # noqa: E402


def bus(spec: dict, base: str, role: str, total: float, channels: int) -> np.ndarray:
    picked = []
    for stem in spec.get("stems", []):
        if stem.get("role") != role:
            continue
        path = stem["file"]
        if not os.path.isabs(path):
            path = os.path.join(base, path)
        wav, sr, _ch, _ = read_wav(path)
        wav = np.asarray(wav, dtype=np.float32)
        if sr != spec.get("sample_rate", sr):
            from semantic_audio_loom.engine import normalize

            wav = normalize._resample(wav, sr, spec["sample_rate"])
        picked.append((wav, float(stem.get("start") or 0.0),
                       float(stem.get("gain_db") or 0.0)))
    a = mix.overlay(picked, spec.get("sample_rate"), total_seconds=total, channels=channels)
    return np.asarray(a.wav, dtype=np.float32)


def rms_db(x: np.ndarray) -> float:
    return float(20 * np.log10(np.sqrt(np.mean(x ** 2) + 1e-12)))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("mix")
    args = ap.parse_args()
    with open(args.mix, encoding="utf-8") as f:
        spec = yaml.safe_load(f)
    base = os.path.dirname(os.path.abspath(args.mix))
    sr = int(spec.get("sample_rate") or 44100)
    channels = int(spec.get("channels") or 1)

    # 声の終わりまで（bed は全体長へ継ぎ足してある）
    voice = bus(spec, base, "voice", 0.0, channels)
    bed = bus(spec, base, "bed", len(voice) / sr, channels)
    if bed.size == 0:
        sys.exit("bed が無い")
    n = min(len(bed), len(voice))
    bed, voice = bed[:n], voice[:n]

    duck_cfg = {"threshold_db": -30.0, "depth_db": 10.0, "attack_s": 0.02,
                "release_s": 0.35, **(spec.get("duck") or {})}
    ducked = mix.duck(bed, voice, sr, **{k: float(v) for k, v in duck_cfg.items()})

    hop = int(0.05 * sr)
    m = n // hop
    env = np.sqrt((voice[: m * hop].reshape(m, hop) ** 2).mean(axis=1) + 1e-12)
    level = 20 * np.log10(env + 1e-9)
    speaking = level > float(duck_cfg["threshold_db"])
    b1 = np.sqrt((bed[: m * hop].reshape(m, hop) ** 2).mean(axis=1) + 1e-12)
    b2 = np.sqrt((ducked[: m * hop].reshape(m, hop) ** 2).mean(axis=1) + 1e-12)
    gain = 20 * np.log10(b2 / b1 + 1e-12)

    print(f"{args.mix}")
    print(f"  bed と voice の重なり {100 * speaking.mean():5.1f}%（声が閾値を超えた時間）")
    print(f"  声の間の bed      {20 * np.log10(np.sqrt(np.mean(b1[~speaking] ** 2))):6.1f} dBFS")
    print(f"  声の上の bed      {20 * np.log10(np.sqrt(np.mean(b2[speaking] ** 2))):6.1f} dBFS")
    print(f"  沈み（中央値）    {np.median(gain[speaking]):6.1f} dB（指定の上限 {duck_cfg['depth_db']:.1f} dB）")
    print(f"  沈み（5%/95%）    {np.percentile(gain[speaking], 5):6.1f} / {np.percentile(gain[speaking], 95):6.1f} dB")


if __name__ == "__main__":
    main()
