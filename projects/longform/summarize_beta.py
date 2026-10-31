#!/usr/bin/env python
"""beta（プロンプト由来の演技成分のノブ）を振ったとき、感情が分かれ始めるか。

同じ台詞・同じ参照音声・同じ seed で beta だけ変える。alpha は 0.35 固定。
分かれ方は「その beta の neutral の 5 seed 中央値に対し、感情の 5 seed が
全部同じ側か（5/5 か 0/5）」で数える。4/5 は seed の揺れと区別できない。

  PYTHONPATH=. <venv> .../summarize_beta.py projects/longform/acting-beta-0{30,50,70}/beta.tsv
"""
from __future__ import annotations

import argparse
import csv
import os
import re
from collections import defaultdict

import numpy as np

METRICS = ["duration", "f0_median_hz", "f0_range_st", "f0_end_st_s",
           "rate_mora_s", "pause_ratio", "energy_median_db", "attack_ms"]
SHORT = {"duration": "長さ", "f0_median_hz": "高さ", "f0_range_st": "抑揚",
         "f0_end_st_s": "語尾", "rate_mora_s": "速さ", "pause_ratio": "間",
         "energy_median_db": "張り", "attack_ms": "出だし"}


def group(path: str) -> str:
    n = path.rsplit("/", 1)[-1].rsplit(".", 1)[0]
    return re.sub(r"-s\d+$", "", n)


def col(rs, m):
    return np.array([float(r[m]) for r in rs])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("tsvs", nargs="+")
    args = ap.parse_args()

    for tsv in args.tsvs:
        beta = os.path.basename(os.path.dirname(tsv))
        with open(tsv, encoding="utf-8") as f:
            rows = list(csv.DictReader(f, delimiter="\t"))
        data: dict[str, list[dict]] = defaultdict(list)
        for r in rows:
            data[group(r["path"])].append(r)
        base = data["neutral"]
        print(f"\n{beta} — {len(rows)} 本")
        print(f"{'感情':8s}" + "".join(f"{SHORT[m]:>16s}" for m in
                                       ["duration", "f0_median_hz", "f0_range_st", "energy_median_db"]))
        for emo in ("neutral", "anger", "joy", "sadness"):
            if emo not in data:
                continue
            print(f"{emo:8s}" + "".join(
                f"{np.median(col(data[emo], m)):9.2f}±{col(data[emo], m).std():5.2f} "
                for m in ["duration", "f0_median_hz", "f0_range_st", "energy_median_db"]))
        for emo in ("anger", "joy", "sadness"):
            if emo not in data:
                continue
            hits = []
            for m in METRICS:
                bm = float(np.median(col(base, m)))
                v = col(data[emo], m)
                up = int((v > bm).sum())
                if up in (0, 5):
                    d = float(np.median(v)) - bm
                    hits.append(f"{SHORT[m]}{'↑' if d > 0 else '↓'}{d:+.2f}")
            print(f"  5/5 で分かれた: {emo:8s} " + ("・".join(hits) if hits else "—"))


if __name__ == "__main__":
    main()
