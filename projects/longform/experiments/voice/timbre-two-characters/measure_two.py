#!/usr/bin/env python
"""同一人物（seed 違い）と別人（同じ台詞・同じ seed）の距離を出す。

  PYTHONPATH=. .venv/bin/python projects/longform/experiments/voice/timbre-two-characters/measure_two.py
"""
from __future__ import annotations

import itertools
import sys

import numpy as np

sys.path.insert(0, "projects/longform")
from measure_timbre import fingerprint  # noqa: E402

BASE = "projects/longform/assets/timbre-two-characters/voice"
LINES = (1, 2, 3)
SPEAKERS = ("mashiro", "niji")
SEEDS = (1, 2, 3)


def main() -> None:
    f = {(li, ch, s): fingerprint(f"{BASE}/l{li}-{ch}-s{s}.wav")
         for li in LINES for ch in SPEAKERS for s in SEEDS}

    def d(a: tuple, b: tuple) -> float:
        return float(np.linalg.norm(f[a] - f[b]))

    same = [d((li, ch, a), (li, ch, b))
            for li in LINES for ch in SPEAKERS for a, b in itertools.combinations(SEEDS, 2)]
    diff = [d((li, a, s), (li, b, s))
            for li in LINES for a, b in itertools.combinations(SPEAKERS, 2) for s in SEEDS]
    for name, xs in (("同一人物", same), ("別人", diff)):
        print(f"{name:6s} {len(xs):2d} 組  中央値 {np.median(xs):5.1f}  範囲 {min(xs):5.1f}–{max(xs):5.1f}")


if __name__ == "__main__":
    main()
