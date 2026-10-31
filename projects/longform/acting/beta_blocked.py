#!/usr/bin/env python
"""beta を 0.7 / 0.5 / 0.3 と振ったとき、感情が seed の揺れを超えるか。

各 beta は 4 感情 × seed 1〜5（同じ台詞・同じ参照）。seed をブロックにした二因子で
感情の効きを測り、**seed を固定したときの感情の幅**と**感情を固定したときの seed の幅**
を同じ物差しで並べる。

  PYTHONPATH=. <venv> .../acting/beta_blocked.py
"""
from __future__ import annotations

import csv
import os
from collections import defaultdict

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
LONGFORM = os.path.dirname(HERE)
BETAS = ["070", "050", "030"]
EMOTIONS = ["neutral", "anger", "joy", "sadness"]
METRICS = [("f0_median_hz", "f0 Hz"), ("f0_range_st", "抑揚 st"),
           ("energy_median_db", "energy dB"), ("rate_mora_s", "速さ")]


def load(beta: str) -> dict[str, dict[str, dict]]:
    path = os.path.join(LONGFORM, f"acting-beta-{beta}", "beta.tsv")
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    data: dict[str, dict[str, dict]] = defaultdict(dict)
    for r in rows:
        name = r["path"].rsplit("/", 1)[-1].rsplit(".", 1)[0]
        k, s = name.rsplit("-s", 1)
        data[k][s] = r
    return data


def blocked(mat: np.ndarray) -> dict:
    r, c = mat.shape
    grand = float(mat.mean())
    row, col = mat.mean(axis=1), mat.mean(axis=0)
    ss_r = float(c * np.sum((row - grand) ** 2))
    ss_c = float(r * np.sum((col - grand) ** 2))
    resid = mat - row[:, None] - col[None, :] + grand
    ss_e = float(np.sum(resid ** 2))
    df_e = (r - 1) * (c - 1)
    ms_e = ss_e / df_e
    f = (ss_r / (r - 1)) / ms_e
    tot = ss_r + ss_c + ss_e
    return {"F": f, "p": float(stats.f.sf(f, r - 1, df_e)),
            "eta_emo": ss_r / tot, "eta_seed": ss_c / tot}


def main() -> None:
    print("感情 4 種 × seed 1〜5。seed をブロックにした二因子（F(3,12) の 5% 点 3.49）")
    for m, label in METRICS:
        print(f"\n--- {label}")
        print(f"{'beta':6s} {'F 感情':>7s} {'p':>8s} {'η² 感情':>8s} {'η² seed':>8s} "
              f"{'感情の幅':>9s} {'seed の幅':>9s}")
        for b in BETAS:
            data = load(b)
            groups = [k for k in EMOTIONS if k in data]
            seeds = sorted({s for k in groups for s in data[k]})
            mat = np.array([[float(data[k][s][m]) for s in seeds] for k in groups])
            r = blocked(mat)
            emo_span = float(np.mean(np.ptp(mat, axis=0)))   # seed ごとの感情の幅
            seed_span = float(np.mean(np.ptp(mat, axis=1)))  # 感情ごとの seed の幅
            print(f"{b:6s} {r['F']:7.2f} {r['p']:8.2g} {r['eta_emo']:8.2f} "
                  f"{r['eta_seed']:8.2f} {emo_span:9.1f} {seed_span:9.1f}")

    # 感情の並びが beta で動くか（f0）
    print("\nf0 の感情の平均（seed 5 本）")
    for b in BETAS:
        data = load(b)
        seeds = sorted({s for k in EMOTIONS for s in data[k]})
        means = {k: float(np.mean([float(data[k][s]["f0_median_hz"]) for s in seeds]))
                 for k in EMOTIONS}
        print(f"  beta 0.{b[1:]}  " + "  ".join(f"{k} {means[k]:.1f}" for k in EMOTIONS))

    # --- 0.3 より下（beta-low・seed 3 本）----------------------------------
    import re
    path = os.path.join(LONGFORM, "acting-beta-low", "low.tsv")
    if not os.path.exists(path):
        return
    with open(path, encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    low: dict[str, dict[str, dict[str, dict]]] = defaultdict(lambda: defaultdict(dict))
    for r in rows:
        m = re.match(r"l(\d{3})-(.+)-s(\d+)$", r["path"].rsplit("/", 1)[-1].rsplit(".", 1)[0])
        low[m.group(1)][m.group(2)][m.group(3)] = r

    print("\n0.3 より下（seed 3 本。F(3,6) の 5% 点 4.76）")
    print(f"{'beta':6s} {'F 感情':>7s} {'p':>8s} {'η² 感情':>8s} {'η² seed':>8s} "
          f"{'感情の幅':>9s} {'seed の幅':>9s}")
    for b in sorted(low):
        seeds = sorted({s for e in low[b].values() for s in e})
        mat = np.array([[float(low[b][e][s]["f0_median_hz"]) for s in seeds]
                        for e in EMOTIONS if e in low[b]])
        r = blocked(mat)
        print(f"0.{b[1:]:<4s} {r['F']:7.2f} {r['p']:8.2g} {r['eta_emo']:8.2f} "
              f"{r['eta_seed']:8.2f} {np.mean(np.ptp(mat, axis=0)):9.1f} "
              f"{np.mean(np.ptp(mat, axis=1)):9.1f}")


if __name__ == "__main__":
    main()
