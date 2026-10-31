#!/usr/bin/env python
"""参照音声から、声のスペクトルがどれだけ離れているかを見る。

**有声フレームだけで測る**（既定）。クリップ全体の平均を取ると、間（無音）の割合が
混ざる——同じ音に無音を 1 秒足しただけで距離が 0 から 39.8 に跳ねる（2026-10-31 実測・
`check_timbre_metric.py`。2 秒で 68.1）。beta を下げると間が減り、有声の割合が上がるので、
全体平均は「演技」と「声そのもの」を混ぜて、声質が遠くなったように見せる。

  PYTHONPATH=. .venv/bin/python projects/longform/measure_timbre.py references/mashiro.wav \
      projects/longform/assets/acting-beta-0*/voice/joy-s1.wav

`--full` を付けると旧来の（無音を含む）測り方になる。比較のため両方を出す。
"""
from __future__ import annotations

import argparse

import librosa
import numpy as np

SR = 24000
N_FFT = 1024
HOP = 240
LOUD_RATIO = 0.05      # 最大フレームの 5% を超えるフレームを「鳴っている」とみなす


def _frames(y: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """MFCC（20 次）と、フレームが鳴っているかの真偽。"""
    S = np.abs(librosa.stft(y, n_fft=N_FFT, hop_length=HOP))
    energy = np.linalg.norm(S, axis=0)
    loud = energy >= LOUD_RATIO * energy.max() if energy.size else np.zeros(0, bool)
    m = librosa.feature.mfcc(y=y, sr=SR, n_mfcc=20, n_fft=N_FFT, hop_length=HOP)
    n = min(m.shape[1], loud.size)
    return m[:, :n], loud[:n]


def fingerprint(path: str, mode: str = "voiced") -> np.ndarray:
    y, _ = librosa.load(path, sr=SR, mono=True)
    m, loud = _frames(y)
    if mode == "voiced" and loud.any():
        m = m[:, loud]
    d = librosa.feature.delta(m)
    return np.concatenate([m.mean(axis=1), d.mean(axis=1)])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("reference")
    ap.add_argument("clips", nargs="+")
    ap.add_argument("--full", action="store_true",
                    help="無音を含む旧来の測り方（有声フレームで切らない）")
    args = ap.parse_args()
    mode = "full" if args.full else "voiced"
    ref = fingerprint(args.reference, mode)
    fps = {p: fingerprint(p, mode) for p in args.clips}
    # 種の中の広がりを物差しにする（1 本との距離だけでは大小が言えない）。
    allv = np.stack(list(fps.values()))
    center = allv.mean(axis=0)
    within = float(np.linalg.norm(allv - center, axis=1).mean())
    print(f"参照 {args.reference} / 本数 {len(fps)} / 種の中の広がり {within:.2f} / "
          f"測り方 {mode}")
    print(f"{'file':52s} {'参照から':>8s}")
    for p, v in fps.items():
        print(f"{p:52s} {float(np.linalg.norm(v - ref)):8.2f}")


if __name__ == "__main__":
    main()
