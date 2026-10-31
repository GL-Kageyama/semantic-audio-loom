#!/usr/bin/env python
"""beta を下げたとき、声そのもの（timbre）が参照音声から離れていないかを見る。

beta は「プロンプト由来の演技成分をどれだけ混ぜるか」のノブなので、下げれば演技は
乗りやすいが、参照音声の声質から離れる恐れがある。MFCC の平均ベクトルで測る。

  .venv/bin/python projects/longform/measure_timbre.py references/mashiro.wav \
      projects/longform/assets/acting-beta-0*/voice/joy-s1.wav
"""
from __future__ import annotations

import argparse

import librosa
import numpy as np


def fingerprint(path: str) -> np.ndarray:
    y, sr = librosa.load(path, sr=24000, mono=True)
    m = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
    d = librosa.feature.delta(m)
    return np.concatenate([m.mean(axis=1), d.mean(axis=1)])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("reference")
    ap.add_argument("clips", nargs="+")
    args = ap.parse_args()
    ref = fingerprint(args.reference)
    fps = {p: fingerprint(p) for p in args.clips}
    # 種の中の広がりを物差しにする（1 本との距離だけでは大小が言えない）。
    allv = np.stack(list(fps.values()))
    center = allv.mean(axis=0)
    within = float(np.linalg.norm(allv - center, axis=1).mean())
    print(f"参照 {args.reference} / 本数 {len(fps)} / 種の中の広がり {within:.2f}")
    print(f"{'file':52s} {'参照から':>8s}")
    for p, v in fps.items():
        print(f"{p:52s} {float(np.linalg.norm(v - ref)):8.2f}")


if __name__ == "__main__":
    main()
