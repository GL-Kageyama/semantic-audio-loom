#!/usr/bin/env python
"""声の「器」（スペクトルの包み）だけを測る。pitch に引っ張られない距離。

`measure_timbre.py` の旧い測り方（クリップ全体の MFCC 平均）では、beta を下げると
距離が大きく動いた（24 → 65）。だが alpha（`alpha × 予測 + (1−alpha) × 参照` の
「予測」に置く重み。上げるほど参照が減る）を 0.35 から 1.0 にしても、その旧い距離は
動かなかった。MFCC の平均は倍音の間隔＝pitch の影響を受けやすく、無音の割合も
混ざるので、「声質が離れた」の証拠にならない疑いがある（有声フレームに直しても、
beta 0.7→0.0 で 60.9→58.0 とほとんど動かない）。

ここでは各フレームの LPC 包絡（声道の共鳴の形）を取り、有声フレームで平均して比べる。
包絡は倍音の間隔を捨てるので、pitch が違っても同じ声道なら近くなる。

  PYTHONPATH=. .venv/bin/python projects/longform/measure_envelope.py \
      references/mashiro.wav projects/longform/assets/foo/voice/*.wav
"""
from __future__ import annotations

import argparse

import librosa
import numpy as np

SR = 24000
N_FFT = 1024
HOP = 240          # 10 ms
GRID = 64          # 包絡を測る周波数の点の数（80〜8000 Hz を対数で）


def envelope(path: str, order: int | None = None) -> np.ndarray:
    """有声フレームの LPC 包絡の平均（dB・各フレームの平均を 0 に正規化）。"""
    y, _ = librosa.load(path, sr=SR, mono=True)
    y = np.asarray(y, dtype=np.float64)
    if y.size < N_FFT:
        y = np.pad(y, (0, N_FFT - y.size))
    # 有声の判定は f0 推定に頼らず、フレームのエネルギーだけで行う（creak でも拾う）。
    frame_db = librosa.amplitude_to_db(
        np.abs(librosa.stft(y, n_fft=N_FFT, hop_length=HOP)), ref=np.max)
    loud = frame_db.mean(axis=0) >= -35.0
    if not loud.any():
        loud = frame_db.mean(axis=0) >= frame_db.mean() - 3.0
    frames = librosa.util.frame(y, frame_length=N_FFT, hop_length=HOP).T
    frames = frames[loud[:len(frames)]]
    frames = frames * np.hanning(N_FFT)
    frames = frames[np.abs(frames).sum(axis=1) > 0]
    if order is None:
        order = 2 + SR // 1000          # 26（24 kHz の声道の共鳴を 2 kHz 幅で拾う）
    freqs = np.geomspace(80.0, 8000.0, GRID)
    angles = 2.0 * np.pi * freqs / SR
    acc = np.zeros(GRID)
    n = 0
    for fr in frames:
        try:
            a = librosa.lpc(fr, order=order)
        except Exception:
            continue
        k = np.arange(len(a))[:, None]
        denom = np.abs((a[:, None] * np.exp(-1j * k * angles[None, :])).sum(axis=0))
        if (denom <= 0).any():
            continue
        db = -20.0 * np.log10(denom)
        db = db - db.mean()
        acc += db
        n += 1
    if n == 0:
        return np.zeros(GRID)
    return acc / n


def distance(a: np.ndarray, b: np.ndarray) -> float:
    """包絡どうしの RMS 差（dB）。"""
    return float(np.sqrt(np.mean((a - b) ** 2)))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("reference")
    ap.add_argument("clips", nargs="+")
    args = ap.parse_args()
    ref = envelope(args.reference)
    print(f"参照 {args.reference}")
    for p in args.clips:
        print(f"{p:64s} 包絡の距離 {distance(ref, envelope(p)):6.2f} dB")


if __name__ == "__main__":
    main()
