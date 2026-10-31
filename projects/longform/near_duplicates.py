#!/usr/bin/env python
"""作品の中の「別々に頼んだのに、ほぼ同じ声になった組」を探す。

`explainer-joy/` で、方向を変えても声質の距離が小さい組があることが分かった
（本番の 2 本は MFCC 5.4）。同じことが他の作品にもあるかを、全キュー総当たりで見る。

物差しは同じ作品の中の分布（中央値・下位 5%）。**しきい値は結果を見る前に決める**:
`--below` の既定 8.0 は、seed を替えたときの揺れ（15〜23）より小さい側。

  PYTHONPATH=. <venv> .../near_duplicates.py projects/longform/assets/drama/voice_trim \
      --script projects/longform/drama/script.yaml [--below 8]

声のファイル名はキュー名（`s01.wav`）。script.yaml から感情・強度・演技の型を引く。
"""
from __future__ import annotations

import argparse
import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
import yaml

from measure_timbre import fingerprint


def _settings(path: str) -> dict[str, dict]:
    data = yaml.safe_load(open(path, encoding="utf-8"))
    out = {}
    for cue in data.get("cues", []):
        name = cue.get("name")
        if name:
            out[name] = {k: cue.get(k) for k in
                         ("character", "emotion", "intensity", "volume", "speed",
                          "delivery", "pitch", "seed")}
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("dir")
    ap.add_argument("--script", required=True)
    ap.add_argument("--below", type=float, default=8.0)
    ap.add_argument("--top", type=int, default=12)
    args = ap.parse_args()

    meta = _settings(args.script)
    names = sorted(n for n in meta if os.path.exists(os.path.join(args.dir, n + ".wav")))
    print(f"{len(names)} 本 / 物差しはこの作品の中の分布")
    fp = {n: fingerprint(os.path.join(args.dir, n + ".wav")) for n in names}

    pairs = []
    for a, b in itertools.combinations(names, 2):
        pairs.append((float(np.linalg.norm(fp[a] - fp[b])), a, b))
    d = np.array([p[0] for p in pairs])
    print(f"組 {len(pairs)} / 中央値 {np.median(d):.2f} / 下位 5% {np.percentile(d, 5):.2f} "
          f"/ 最小 {d.min():.2f}")

    pairs.sort()
    print(f"\n近い組 {args.top}（{args.below} 未満は ⚠）:")
    for dist, a, b in pairs[:args.top]:
        ma, mb = meta[a], meta[b]
        mark = "⚠" if dist < args.below else " "
        print(f"{mark} {dist:6.2f}  {a}↔{b}  "
              f"[{ma['character']} {ma['emotion']}/{ma['intensity']}/{ma['volume']}/{ma['speed']}/{ma['delivery']}]"
              f" / [{mb['character']} {mb['emotion']}/{mb['intensity']}/{mb['volume']}/{mb['speed']}/{mb['delivery']}]")


if __name__ == "__main__":
    main()
