#!/usr/bin/env python
"""11 感情（moderate）と強度（subtle/strong）を seed 5 で読み直す。

判定 1：基準線（neutral moderate）の 5 seed 中央値に対して、種の 5 seed が
        全部同じ側か（5/5 か 0/5）。4/5 は seed の揺れと区別できない。
判定 2：その差が基準線そのものの幅（max−min）より大きいか。5/5 でも
        幅に埋もれる差は「分かれた」とは呼ばない。

  PYTHONPATH=. <venv> .../summarize_matrix.py projects/longform/acting-matrix/matrix.tsv
"""
from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict

import numpy as np

METRICS = ["duration", "f0_median_hz", "f0_range_st", "f0_end_st_s",
           "rate_mora_s", "pause_ratio", "energy_median_db", "attack_ms"]
SHORT = {"duration": "長さ", "f0_median_hz": "高さ", "f0_range_st": "抑揚",
         "f0_end_st_s": "語尾", "rate_mora_s": "速さ", "pause_ratio": "間",
         "energy_median_db": "張り", "attack_ms": "出だし"}


def name_of(path: str) -> str:
    return path.rsplit("/", 1)[-1].rsplit(".", 1)[0]


def split(name: str) -> tuple[str, str]:
    """名前 → (群, seed)。em-joy-s3 → (em-joy, 3)。"""
    m = re.match(r"(.*)-s(\d+)$", name)
    return (m.group(1), m.group(2)) if m else (name, "")


def col(rs, m):
    return np.array([float(r[m]) for r in rs])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("tsv")
    args = ap.parse_args()
    with open(args.tsv, encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    data: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        data[split(name_of(r["path"]))[0]].append(r)

    base = sorted(data["baseline"], key=lambda r: split(name_of(r["path"]))[1])
    bmed = {m: float(np.median(col(base, m))) for m in METRICS}
    bwidth = {m: float(col(base, m).max() - col(base, m).min()) for m in METRICS}

    print(f"{args.tsv} — {len(rows)} 本 / {len(data)} 群 / 1 群 {len(base)} seed")
    print("基準線（neutral moderate・5 seed）")
    print("  " + "  ".join(f"{SHORT[m]} {bmed[m]:.2f}（幅 {bwidth[m]:.2f}）" for m in METRICS))

    print("\n【感情 × moderate】5/5 か 0/5 で片側に寄った指標")
    print("  ✓ = 差が基準線の幅より大きい / △ = 5/5 だが幅に埋もれる")
    for g in sorted(k for k in data if k.startswith("em-")):
        hits = []
        for m in METRICS:
            v = col(data[g], m)
            up = int((v > bmed[m]).sum())
            if up not in (0, 5):
                continue
            d = float(np.median(v)) - bmed[m]
            mark = "✓" if abs(d) > bwidth[m] else "△"
            hits.append(f"{mark}{SHORT[m]}{'↑' if d > 0 else '↓'}{d:+.2f}")
        print(f"  {g[3:]:12s} " + ("・".join(hits) if hits else "—"))

    print("\n【強度】同じ seed どうしで strong − subtle の符号が 5/5 揃った指標")
    for emo in ("anger", "joy", "sadness"):
        thin, thick = data.get(f"in-{emo}-subtle"), data.get(f"in-{emo}-strong")
        if not thin or not thick:
            continue
        hits = []
        for m in METRICS:
            key = {split(name_of(r["path"]))[1]: float(r[m]) for r in thin}
            diffs = [float(r[m]) - key[split(name_of(r["path"]))[1]]
                     for r in thick if split(name_of(r["path"]))[1] in key]
            if len(diffs) != 5:
                continue
            if all(d > 0 for d in diffs) or all(d < 0 for d in diffs):
                d = float(np.median(col(thick, m)) - np.median(col(thin, m)))
                mark = "✓" if abs(d) > bwidth[m] else "△"
                hits.append(f"{mark}{SHORT[m]}{'↑' if d > 0 else '↓'}{d:+.2f}")
        print(f"  {emo:8s} " + ("・".join(hits) if hits else "—"))


if __name__ == "__main__":
    main()
