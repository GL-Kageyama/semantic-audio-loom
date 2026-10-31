#!/usr/bin/env python3
"""強度（intensity）の 3 段は、声を段で動かすか。

experiments/basics/acting-matrix/matrix.tsv の既存 85 本から、同じ感情の 3 段を並べる。
  subtle    = in-<emotion>-subtle
  moderate  = em-<emotion>
  strong    = in-<emotion>-strong
seed は 1〜5 の 5 本。基準線は baseline-s<seed>（neutral / moderate）。

測るもの（すべて基準線の同じ seed からの差）:
  f0  … f0_median_hz の差（Hz）
  en  … energy_median_db の差（dB）
  rt  … rate_mora_s の比（倍）

検定: 段を列・seed を行にした二元配置（反復なし）。
  誤差の自由度 = (3-1)(5-1) = 8。seed はブロック（同じ seed の中で段を比べる）。
  段の効果が seed の癖に飲まれていないかを見るため。
"""
import csv
import os
import sys

import numpy as np
from scipy import stats

HERE = os.path.dirname(os.path.abspath(__file__))
LONGFORM = os.path.dirname(HERE)
MATRIX = os.path.join(LONGFORM, "experiments", "basics", "acting-matrix", "matrix.tsv")
OVER = os.path.join(LONGFORM, "experiments", "intensity", "acting-overwhelming-070", "probe.tsv")

EMOTIONS = ["anger", "joy", "sadness"]
LEVELS = [("subtle", "in-%s-subtle"), ("moderate", "em-%s"), ("strong", "in-%s-strong"),
          ("overwhelming", "ov-%s")]
SEEDS = ["1", "2", "3", "4", "5"]


def load():
    by_name = {}
    for path in (MATRIX, OVER):
        if not os.path.exists(path):
            continue
        rows = list(csv.DictReader(open(path, encoding="utf-8"), delimiter="\t"))
        for r in rows:
            name = os.path.basename(r["path"]).rsplit(".", 1)[0]
            by_name[name] = {k: float(v) for k, v in r.items() if k not in ("path",)}
    return by_name


def blocked(mat):
    """二元配置（反復なし）。行 = seed、列 = 段。"""
    r, c = mat.shape
    grand = float(mat.mean())
    row = mat.mean(axis=1)
    col = mat.mean(axis=0)
    resid = mat - row[:, None] - col[None, :] + grand
    ss_err = float(np.sum(resid ** 2))
    df_err = (r - 1) * (c - 1)
    ms_err = ss_err / df_err
    ss_col = float(r * np.sum((col - grand) ** 2))
    ss_row = float(c * np.sum((row - grand) ** 2))
    return {
        "F": (ss_col / (c - 1)) / ms_err if ms_err > 0 else float("inf"),
        "df1": c - 1,
        "df2": df_err,
        "ss_col": ss_col,
        "ss_row": ss_row,
        "ss_err": ss_err,
        "ms_err": ms_err,
    }


def line2() -> None:
    """2 行目「そんなこと、ないよ。」の 4 段 × 3 感情 × 5 seed。

    基準線を置かず、同じ感情・同じ seed の中で段を比べる（感情の効きは別の実験）。
    """
    path = os.path.join(LONGFORM, "experiments", "intensity", "acting-intensity-line2", "probe.tsv")
    d = {}
    for r in csv.DictReader(open(path, encoding="utf-8"), delimiter="\t"):
        name = os.path.basename(r["path"]).rsplit(".", 1)[0]
        d[name] = {k: float(v) for k, v in r.items() if k not in ("path",)}

    print("2 行目「そんなこと、ないよ。」f0 中央値（seed 5 の平均）\n")
    print(f"{'感情':10s}" + "".join(f"{label:>14s}" for label, _ in LEVELS))
    for emo in EMOTIONS:
        vals = [np.mean([d[f"l2-{emo}-{label}-s{s}"]["f0_median_hz"] for s in SEEDS[0:5]])
                for label, _ in LEVELS]
        print(f"{emo:10s}" + "".join(f"{v:14.1f}" for v in vals))

    print("\n--- 隣り合う段の差（seed ごとに対にする）---")
    for emo in EMOTIONS:
        for (la, _), (lb, _) in zip(LEVELS, LEVELS[1:]):
            diff = np.array([d[f"l2-{emo}-{lb}-s{s}"]["f0_median_hz"]
                             - d[f"l2-{emo}-{la}-s{s}"]["f0_median_hz"] for s in SEEDS[0:5]])
            t, p = stats.ttest_1samp(diff, 0.0)
            sign = sum(1 for x in diff if x > 0)
            print(f"{emo:9s}{la:9s}→ {lb:13s}{np.mean(diff):+7.1f} Hz  "
                  f"t = {t:+5.2f}  p = {p:.4f}  同符号 {sign}/{len(diff)}")
        print()


def main():
    if "--line2" in sys.argv:
        line2()
        return
    d = load()
    print("強度の 3 段（同じ感情・同じ seed の中で比べる）\n")
    print("感情     段        f0 差       energy 差   速さ比")
    for emo in EMOTIONS:
        for label, key in LEVELS:
            f = []
            e = []
            rt = []
            for s in SEEDS:
                cue = d[key % emo + "-s" + s]
                base = d["baseline-s" + s]
                f.append(cue["f0_median_hz"] - base["f0_median_hz"])
                e.append(cue["energy_median_db"] - base["energy_median_db"])
                rt.append(cue["rate_mora_s"] / base["rate_mora_s"])
            mark = "" if label != "moderate" else "  ← 3 段の真ん中"
            print(f"{emo:9s}{label:9s}{np.mean(f):+7.1f} Hz  {np.mean(e):+7.1f} dB  {np.mean(rt):5.2f}×{mark}")
        print()

    print("--- 段は seed をブロックしても効くか（f0 差の二元配置）---")
    for emo in EMOTIONS:
        mat = np.zeros((len(SEEDS), len(LEVELS)))
        for i, s in enumerate(SEEDS):
            base = d["baseline-s" + s]
            for j, (label, key) in enumerate(LEVELS):
                mat[i, j] = d[key % emo + "-s" + s]["f0_median_hz"] - base["f0_median_hz"]
        a = blocked(mat)
        p = float(stats.f.sf(a["F"], a["df1"], a["df2"]))
        eta = a["ss_col"] / (a["ss_col"] + a["ss_row"] + a["ss_err"])
        print(f"{emo:9s}F({a['df1']},{a['df2']}) = {a['F']:7.2f}  p = {p:.4f}  η²(段) = {eta:.2f}")

    print("\n--- 隣り合う段の差（seed ごとの差を 5 本そろえて t 検定）---")
    pairs = [("subtle", 0, "moderate", 1), ("moderate", 1, "strong", 2),
             ("subtle", 0, "strong", 2), ("strong", 2, "overwhelming", 3)]
    for emo in EMOTIONS:
        for la, ia, lb, ib in pairs:
            diff = []
            for s in SEEDS:
                base = d["baseline-s" + s]
                a = d[LEVELS[ia][1] % emo + "-s" + s]["f0_median_hz"] - base["f0_median_hz"]
                b = d[LEVELS[ib][1] % emo + "-s" + s]["f0_median_hz"] - base["f0_median_hz"]
                diff.append(b - a)
            diff = np.array(diff)
            t, p = stats.ttest_1samp(diff, 0.0)  # 段の差が 0 か（seed 5 本の 1 標本）
            sign = sum(1 for x in diff if x > 0)
            print(f"{emo:9s}{la:9s}→ {lb:9s}{np.mean(diff):+7.1f} Hz  "
                  f"t = {t:+5.2f}  p = {p:.4f}  同符号 {sign}/{len(diff)}")
        print()


if __name__ == "__main__":
    main()
