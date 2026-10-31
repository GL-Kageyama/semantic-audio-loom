#!/usr/bin/env python
"""seed の癖は、声をまたぐか（4 つの声 × seed 1〜3・同じ 1 行）。

絶対の高さは声で違うので、見るのは**声ごとの seed のずれ**（その声の 3 seed の平均から）。
s1 が高い、が 4 つの声で同じ向きなら「seed は声をまたぐ癖」、ばらばらなら
「seed と声の交互作用」。

  PYTHONPATH=. <venv> .../measure_seed_voices.py
"""
from __future__ import annotations

import itertools
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__)))))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "projects", "longform"))

import numpy as np

from semantic_audio_loom.skills.act_probe import measure as probe
from measure_timbre import fingerprint

HERE = os.path.dirname(os.path.abspath(__file__))
VOICE = os.path.join(os.path.dirname(HERE), "assets", "seed-voices", "voice")

VOICES = ["narrator", "mashiro", "niji", "katari"]
SEEDS = [1, 2, 3]
LABEL = {"narrator": "narrator（語り手）", "mashiro": "mashiro（真白）",
         "niji": "niji（ニジ）", "katari": "katari（午前二時の語り）"}


def path(v: str, s: int) -> str:
    return os.path.join(VOICE, f"{v}-s{s}.wav")


def main() -> None:
    missing = [path(v, s) for v in VOICES for s in SEEDS if not os.path.exists(path(v, s))]
    if missing:
        sys.exit("先に build_voice.py --dir projects/longform/seed-voices を走らせる:\n  "
                 + "\n  ".join(missing))

    m = {(v, s): probe(path(v, s)) for v in VOICES for s in SEEDS}
    print(f"{'声':24s} {'seed':>5s} {'f0':>7s} {'抑揚':>6s} {'速さ':>6s} {'energy':>7s}")
    for v in VOICES:
        for s in SEEDS:
            x = m[(v, s)]
            print(f"{LABEL[v]:24s} {s:5d} {x['f0_median_hz']:7.1f} {x['f0_range_st']:6.1f} "
                  f"{x['rate_mora_s']:6.1f} {x['energy_median_db']:7.1f}")

    # 声ごとの seed のずれ
    print(f"\n{'声':24s} {'平均 f0':>8s} {'s1−平均':>8s} {'s2−平均':>8s} {'s3−平均':>8s} {'幅':>6s}")
    off = {}
    for v in VOICES:
        vals = np.array([m[(v, s)]["f0_median_hz"] for s in SEEDS])
        mu = float(vals.mean())
        off[v] = vals - mu
        print(f"{LABEL[v]:24s} {mu:8.1f} {off[v][0]:8.1f} {off[v][1]:8.1f} "
              f"{off[v][2]:8.1f} {np.ptp(vals):6.1f}")

    # ずれの向きは声をまたいで同じか
    print("\nずれの符号（+ = その声の平均より高い）")
    for v in VOICES:
        print(f"  {LABEL[v]:24s} " + " ".join("+" if x > 0 else "−" for x in off[v]))
    same = all((off[v][0] > 0) == (off[VOICES[0]][0] > 0) for v in VOICES)
    print(f"  s1 の符号が 4 つの声で同じ: {'はい' if same else 'いいえ'}")

    if len(VOICES) > 2:
        tab = np.array([[off[v][i] for i in range(3)] for v in VOICES])
        rho = np.corrcoef(tab)
        print("  ずれの相関（声どうし）: "
              + " / ".join(f"{a[:4]}–{b[:4]} {rho[i, j]:.2f}"
                           for i, a in enumerate(VOICES) for j, b in enumerate(VOICES) if i < j))

    # 音色：seed が声の中で動かす量 vs 声どうしの距離
    fp = {(v, s): fingerprint(path(v, s)) for v in VOICES for s in SEEDS}
    within = {v: float(np.mean([np.linalg.norm(fp[(v, a)] - fp[(v, b)])
                                for a, b in itertools.combinations(SEEDS, 2)]))
              for v in VOICES}
    cent = {v: np.mean([fp[(v, s)] for s in SEEDS], axis=0) for v in VOICES}
    across = [float(np.linalg.norm(cent[a] - cent[b]))
              for a, b in itertools.combinations(VOICES, 2)]
    print("\n音色（MFCC・有声フレーム）")
    print("  seed を替えたとき（声の中）: "
          + " / ".join(f"{v} {d:.1f}" for v, d in within.items()))
    print(f"  声どうし（seed 3 本の重心）: 中央 {np.median(across):.1f}"
          f"（{min(across):.1f}〜{max(across):.1f}）")


if __name__ == "__main__":
    main()
