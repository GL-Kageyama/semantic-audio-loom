#!/usr/bin/env python
"""alpha（参照音声の声質をどれだけ保つかのノブ）を振ったときの、演技と声質の両方を見る。

`inference` の中では `ref = alpha * 予測 + (1 - alpha) * 参照` なので、alpha を上げると
参照音声の声質から離れ、下げると近づく。beta は 0.3 固定（演技が乗る側）。

演技の分かれ方は「その alpha の neutral の seed 中央値に対し、感情の seed が全部
同じ側か（3/3 か 0/3）」で数える。声質は `references/mashiro.wav` との MFCC 距離。

  PYTHONPATH=. <venv> .../summarize_alpha.py projects/longform/acting-alpha/alpha.tsv \
      references/mashiro.wav
"""
from __future__ import annotations

import argparse
import csv
import re
from collections import defaultdict

import librosa
import numpy as np

METRICS = ["f0_median_hz", "f0_range_st", "f0_end_st_s",
           "rate_mora_s", "pause_ratio", "energy_median_db", "attack_ms"]
SHORT = {"f0_median_hz": "高さ", "f0_range_st": "抑揚", "f0_end_st_s": "語尾",
         "rate_mora_s": "速さ", "pause_ratio": "間", "energy_median_db": "張り",
         "attack_ms": "出だし"}
DIR = "projects/longform/assets/acting-alpha/voice"


def fingerprint(path: str) -> np.ndarray:
    y, sr = librosa.load(path, sr=24000, mono=True)
    m = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=20)
    d = librosa.feature.delta(m)
    return np.concatenate([m.mean(axis=1), d.mean(axis=1)])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("tsv")
    ap.add_argument("reference")
    args = ap.parse_args()

    with open(args.tsv, encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    # a020-anger-s1 → (0.20, anger, 1)
    data: dict[tuple[str, str], list[dict]] = defaultdict(list)
    names: dict[tuple[str, str], list[str]] = defaultdict(list)
    for r in rows:
        stem = r["path"].rsplit("/", 1)[-1].rsplit(".", 1)[0]
        m = re.match(r"a(\d+)-(\w+)-s(\d+)$", stem)
        tag, emo = m.group(1), m.group(2)
        data[(tag, emo)].append(r)
        names[(tag, emo)].append(stem)
    tags = sorted({k[0] for k in data})

    ref = fingerprint(args.reference)
    fps = {n: fingerprint(f"{DIR}/{n}.wav") for v in names.values() for n in v}
    # 物差し：同じ alpha の中でどれだけ散っているか（参照との距離だけでは大小が言えない）。
    for k, v in names.items():
        allv = np.stack([fps[n] for n in v])
        spread = float(np.linalg.norm(allv - allv.mean(axis=0), axis=1).mean())
        print(f"{k[0]} {k[1]:8s} 参照から {np.mean([np.linalg.norm(fps[n] - ref) for n in v]):5.1f}"
              f" / 中の広がり {spread:5.1f}")

    print(f"\n{'alpha':6s} {'neutral':>8s} {'sadness':>8s} {'anger':>8s} {'joy':>8s}"
          f"  {'分かれた指標（3/3）':s}")
    for tag in tags:
        a = int(tag) / 100
        med = {e: float(np.median([float(r["f0_median_hz"]) for r in data[(tag, e)]]))
               for e in ("neutral", "sadness", "anger", "joy")}
        hits = []
        for emo in ("anger", "joy", "sadness"):
            for m in METRICS:
                up = sum(float(r[m]) > float(b[m])
                         for r, b in zip(data[(tag, emo)], data[(tag, "neutral")]))
                if up in (0, 3):
                    hits.append(f"{emo}.{SHORT[m]}{'↑' if up == 3 else '↓'}")
        print(f"{a:<6.2f} {med['neutral']:8.1f} {med['sadness']:8.1f} {med['anger']:8.1f}"
              f" {med['joy']:8.1f}  {'・'.join(hits) if hits else '—'}")


if __name__ == "__main__":
    main()
