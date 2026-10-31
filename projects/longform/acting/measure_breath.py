"""息の混ざり具合を測る（breathiness の欄が声に届くかを見るため）。

有声とみなすフレーム（rms ≥ 0.02）だけで、2.5〜8 kHz のエネルギーが
100 Hz〜8 kHz の全体に占める割合を出す。息（雑音）が増えると、この比が上がる。
無音のフレームを混ぜないので、前後の無音の長さでは動かない。

`bin/act_probe.py` の `voiced_fraction`（有声フレームの割合）と合わせて読む。

使い方:
    PYTHONPATH=. <venv> projects/longform/acting/measure_breath.py <wav...>
"""
from __future__ import annotations

import sys
import wave

import numpy as np

FRAME_S = 0.04
HOP_RATIO = 0.5
ACTIVE_RMS = 0.02
BAND = (100.0, 8000.0)
HF = (2500.0, 8000.0)


def load(path: str) -> tuple[np.ndarray, int]:
    with wave.open(path) as w:
        sr = w.getframerate()
        n = w.getnframes()
        x = np.frombuffer(w.readframes(n), dtype=np.int16).astype(np.float32) / 32768.0
    return x, sr


def hf_ratio(path: str) -> float:
    """有声フレームの中央値（外れ値に強い）。"""
    x, sr = load(path)
    n = len(x)
    F = int(FRAME_S * sr)
    H = int(F * HOP_RATIO)
    ratios = []
    for i in range(0, max(0, n - F + 1), H):
        fr = x[i:i + F]
        if float(np.sqrt(np.mean(fr**2))) < ACTIVE_RMS:
            continue
        sp = np.abs(np.fft.rfft(fr * np.hanning(F))) ** 2
        f = np.fft.rfftfreq(F, 1.0 / sr)
        tot = float(sp[(f > BAND[0]) & (f < BAND[1])].sum())
        hi = float(sp[(f > HF[0]) & (f < HF[1])].sum())
        if tot > 0.0:
            ratios.append(hi / tot)
    return float(np.median(ratios)) if ratios else float("nan")


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 2
    print("path\thf_ratio")
    for p in argv:
        print(f"{p}\t{hf_ratio(p):.5f}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
