#!/usr/bin/env python
"""seed と演技の方向、どちらが声を動かすか（真白・同じ 1 行「明日、また来るね。」）。

本番の 2 本（m02 = 励まし・m04 = 照れ隠し）と、同じ設定で seed を 2・3 へ振った本、
方向を強く振った 3 本を並べて測る。

  PYTHONPATH=. <venv> .../measure_joy.py

出すもの:
- 包絡の距離（measure_envelope・LPC 26 次・dB・RMS）と MFCC の距離（measure_timbre）
- act_probe の 6 指標（f0 中央値・抑揚・速さ・間・energy・有声率）
"""
from __future__ import annotations

import itertools
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "projects", "longform"))   # measure_*.py はここ

import numpy as np

from semantic_audio_loom.skills.act_probe import measure as probe
from measure_envelope import distance, envelope
from measure_timbre import fingerprint

HERE = os.path.dirname(os.path.abspath(__file__))


def _lf_root(d=HERE):
    """projects/longform の根まで上へ辿る（REPORT.md と assets のある所）。"""
    while not os.path.exists(os.path.join(d, "REPORT.md")):
        d = os.path.dirname(d)
    return d

ASSETS = os.path.join(_lf_root(), "assets")
PROD = os.path.join(ASSETS, "explainer", "voice")
JOY = os.path.join(ASSETS, "explainer-joy", "voice")

FILES = [
    ("本番 m02 励まし s1", os.path.join(PROD, "m02.wav")),
    ("本番 m04 照れ隠し s1", os.path.join(PROD, "m04.wav")),
    ("m02 の設定 s2", os.path.join(JOY, "a02-s2.wav")),
    ("m02 の設定 s3", os.path.join(JOY, "a02-s3.wav")),
    ("m04 の設定 s2", os.path.join(JOY, "a04-s2.wav")),
    ("m04 の設定 s3", os.path.join(JOY, "a04-s3.wav")),
    ("alt quiet/slow/hesitant", os.path.join(JOY, "alt-slow.wav")),
    ("alt very_slow/cheerful", os.path.join(JOY, "alt-vslow.wav")),
    ("alt neutral/gentle", os.path.join(JOY, "alt-neutral.wav")),
]


def main() -> None:
    missing = [p for _, p in FILES if not os.path.exists(p)]
    if missing:
        sys.exit("先に build_voice.py --dir projects/longform/experiments/scene/explainer-joy を走らせる:\n  "
                 + "\n  ".join(missing))

    print(f"{'':26s} {'f0':>7s} {'抑揚':>6s} {'速さ':>6s} {'間':>6s} {'energy':>7s}")
    for label, path in FILES:
        m = probe(path)
        print(f"{label:26s} {m['f0_median_hz']:7.1f} {m['f0_range_st']:6.1f} "
              f"{m['rate_mora_s']:6.1f} {m['pause_ratio']:6.3f} {m['energy_median_db']:7.1f}")

    env = {label: envelope(path) for label, path in FILES}
    fp = {label: fingerprint(path) for label, path in FILES}
    print(f"\n{'対':52s} {'包絡 dB':>8s} {'MFCC':>7s}")
    for a, b in itertools.combinations([lab for lab, _ in FILES], 2):
        print(f"{a + ' ↔ ' + b:52s} {distance(env[a], env[b]):8.2f} "
              f"{float(np.linalg.norm(fp[a] - fp[b])):7.2f}")


if __name__ == "__main__":
    main()
