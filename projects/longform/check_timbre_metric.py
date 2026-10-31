#!/usr/bin/env python
"""`measure_timbre.py` の距離が、無音の割合に汚されていないかを確かめる。

同じ音に無音を足すだけなら、声は 1 ビットも変わっていない。距離が動いたら、
その計器は声質ではなく「鳴っていない時間の長さ」を測っている。

  PYTHONPATH=. .venv/bin/python projects/longform/check_timbre_metric.py
"""
from __future__ import annotations

import sys

import librosa
import numpy as np

sys.path.insert(0, "projects/longform")
from measure_timbre import fingerprint  # noqa: E402

SR = 24000


def main() -> None:
    y, _ = librosa.load("references/mashiro.wav", sr=SR, mono=True)
    base = fingerprint("references/mashiro.wav")
    base_full = fingerprint("references/mashiro.wav", mode="full")
    print(f"{'足した無音':>10s} {'有声フレーム':>12s} {'クリップ全体':>12s}")
    for extra in (0.0, 0.5, 1.0, 2.0):
        pad = np.zeros(int(extra * SR))
        p = f"/tmp/silence-probe-{extra:.1f}.wav"
        _write(p, y, pad, SR)
        v = float(np.linalg.norm(fingerprint(p) - base))
        f = float(np.linalg.norm(fingerprint(p, mode="full") - base_full))
        print(f"{extra:8.1f} s {v:12.2f} {f:12.2f}")


def _write(path: str, y: np.ndarray, pad: np.ndarray, sr: int) -> None:
    import soundfile as sf

    sf.write(path, np.concatenate([y, pad]) if pad.size else y, sr)


if __name__ == "__main__":
    main()
