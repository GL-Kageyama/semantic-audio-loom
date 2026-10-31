#!/usr/bin/env python
"""P2 の 55 本（枠外 10 種 × seed 1〜5）を、seed をブロックにして読み直す。

`summarize_seeds.py` は「同じ種の 5 seed が、基準線の**中央値**より上/下に出た数」を
数える。だが seed は毎回ばらけるのでなく **seed ごとに決まった高さへ寄る**ので、
この数え方は演技の差を揺れに埋める（`../../emotion-seed/` で実測）。

ここでは seed をブロックとして除き、種の効きを分散分析で見る。さらに基準線との
差を、ブロック後の誤差で検定する（Bonferroni で 10 種ぶん補正）。

  PYTHONPATH=. <venv> .../reanalyze_seeds.py projects/longform/acting/seeds.tsv
"""
from __future__ import annotations

import argparse
import csv
from collections import defaultdict

import numpy as np
from scipy import stats

METRICS = [
    ("duration", "長さ s"),
    ("f0_median_hz", "f0 Hz"),
    ("f0_range_st", "抑揚 st"),
    ("rate_mora_s", "速さ mora/s"),
    ("pause_ratio", "間"),
    ("energy_median_db", "energy dB"),
    ("voiced_fraction", "有声率"),
    ("attack_ms", "立ち上がり ms"),
]


def kind_of(path: str) -> str:
    name = path.rsplit("/", 1)[-1].rsplit(".", 1)[0]
    return name.rsplit("-s", 1)[0]


def seed_of(path: str) -> str:
    return path.rsplit("/", 1)[-1].rsplit(".", 1)[0].rsplit("-s", 1)[1]


def blocked(mat: np.ndarray) -> dict:
    """反復なし二因子（行＝種・列＝seed）。eta は寄与率。"""
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
    p = float(stats.f.sf(f, r - 1, df_e))
    tot = ss_r + ss_c + ss_e
    return {"F": f, "p": p, "df": (r - 1, df_e), "ms_e": ms_e,
            "eta_kind": ss_r / tot, "eta_seed": ss_c / tot}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("tsv")
    args = ap.parse_args()

    with open(args.tsv, encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    data: dict[str, dict[str, dict]] = defaultdict(dict)
    for r in rows:
        data[kind_of(r["path"])][seed_of(r["path"])] = r
    kinds = sorted(data)
    seeds = sorted({s for d in data.values() for s in d})
    full = [k for k in kinds if len(data[k]) == len(seeds)]
    print(f"{args.tsv} — {len(full)} 種 × {len(seeds)} seed（全欄が揃った種だけ）")

    # --- 種の効き（seed をブロック）-----------------------------------------
    df_kind = len(full) - 1
    df_seed = len(seeds) - 1
    df_err = df_kind * df_seed
    print(f"\nseed をブロックにした二因子（F({df_kind},{df_err}) の 5% 点 "
          f"{float(stats.f.isf(0.05, df_kind, df_err)):.2f}）")
    print(f"{'指標':14s} {'F 種':>8s} {'p':>9s} {'η² 種':>7s} {'η² seed':>8s}")
    meta = {}
    for m, label in METRICS:
        mat = np.array([[float(data[k][s][m]) for s in seeds] for k in full])
        r = blocked(mat)
        meta[m] = r
        print(f"{label:14s} {r['F']:8.2f} {r['p']:9.2g} {r['eta_kind']:7.2f} "
              f"{r['eta_seed']:8.2f}")

    # --- 基準線との差（ブロック後の誤差で）----------------------------------
    n = len(seeds)
    t_crit = float(stats.t.isf(0.05 / (2 * (len(full) - 1)), meta["duration"]["df"][1]))
    print(f"\n基準線との差（t。Bonferroni 10 種で |t| >{t_crit:.2f} を採る）")
    for m, label in METRICS:
        ms_e = meta[m]["ms_e"]
        se = np.sqrt(2 * ms_e / n)
        if se == 0:
            continue
        lines = []
        for k in full:
            if k == "baseline":
                continue
            d = float(np.mean([float(data[k][s][m]) for s in seeds])) \
                - float(np.mean([float(data["baseline"][s][m]) for s in seeds]))
            t = d / se
            if abs(t) > t_crit:
                lines.append(f"{k} {d:+.2f}（t {t:+.1f}）")
        print(f"  {label:14s} " + (" / ".join(lines) if lines else "— どの種も超えない"))

    # --- 同じ seed どうしで比べる（seed をそろえた対応のある比較）-----------
    print("\n同じ seed どうしで見た向き（5/5 か 0/5 の種だけ）")
    for m, label in METRICS:
        ups = []
        for k in full:
            if k == "baseline":
                continue
            c = sum(1 for s in seeds if float(data[k][s][m]) > float(data["baseline"][s][m]))
            if c in (0, len(seeds)):
                ups.append(("↑" if c else "↓") + k)
        print(f"  {label:14s} " + (" ".join(ups) if ups else "—"))

    # --- f0 の上がり幅（種ごと）--------------------------------------------
    print("\nf0 の上がり幅（基準線の同じ seed から）")
    for k in full:
        if k == "baseline":
            continue
        d = [float(data[k][s]["f0_median_hz"]) - float(data["baseline"][s]["f0_median_hz"])
             for s in seeds]
        print(f"  {k:11s} {np.mean(d):+6.1f} Hz（{min(d):+.1f}〜{max(d):+.1f}）")


if __name__ == "__main__":
    main()
