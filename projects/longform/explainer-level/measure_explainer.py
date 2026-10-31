#!/usr/bin/env python
"""解説「音は、なぜ感情を動かすのか」を、キューごとに測る。

  PYTHONPATH=. .venv/bin/python projects/longform/explainer-level/measure_explainer.py

語り手 44 本と、実例の真白 4 本（同じ台詞「明日、また来るね。」を 4 通り）。
見るのは二つ：

1. 演技の指標（act_probe）をキューごとに。出力は probe.tsv。
2. 声の器（LPC 包絡）の距離。**4 通りの演技の差**と、**語り手と真白の差**の
   どちらが大きいか。どちらも同じ計器（measure_envelope.py）で測る。
"""
from __future__ import annotations

import csv
import itertools
import os
import statistics
import sys

import numpy as np
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(BASE))
sys.path.insert(0, ROOT)

from projects.longform.measure_envelope import distance, envelope  # noqa: E402
from semantic_audio_loom.skills import act_probe  # noqa: E402

METRICS = ("f0_median_hz", "f0_range_st", "rate_mora_s", "pause_ratio",
           "energy_median_db", "voiced_fraction")
REFS = {"narrator": "female_mature_p294", "mashiro": "mashiro"}


def main() -> None:
    cues = yaml.safe_load(open(os.path.join(BASE, "explainer", "script.yaml")))["cues"]
    vdir = os.path.join(BASE, "assets", "explainer", "voice")
    rows = []
    env: dict[str, dict[str, list[float]]] = {"narrator": {}, "mashiro": {}}
    for c in cues:
        path = os.path.join(vdir, c["name"] + ".wav")
        if not os.path.exists(path):
            print(f"無し: {path}", file=sys.stderr)
            continue
        e = act_probe.measure(path)
        rows.append({
            "name": c["name"], "character": c["character"], "emotion": c["emotion"],
            "intensity": c["intensity"], "volume": c["volume"], "speed": c["speed"],
            "delivery": c["delivery"], "duration": e["duration"],
            **{k: e[k] for k in METRICS},
        })
        env[c["character"]][c["name"]] = envelope(path)
    out = os.path.join(HERE, "probe.tsv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter="\t")
        w.writeheader()
        w.writerows(rows)
    print(f"{out}: {len(rows)} 行")

    def centroid(group: dict[str, list[float]]) -> np.ndarray:
        return np.mean(np.stack(list(group.values())), axis=0)

    def pairs(group: dict[str, list[float]]) -> list[float]:
        return [distance(a, b) for a, b in itertools.combinations(group.values(), 2)]

    refs = {k: envelope(os.path.join(ROOT, "references", v + ".wav")) for k, v in REFS.items()}
    nar, mas = env["narrator"], env["mashiro"]
    cn, cm = centroid(nar), centroid(mas)
    print(f"\n包絡（LPC 26 次・64 点・dB・RMS 距離）")
    print(f"  語り手 {len(nar)} 本の中心 ↔ 真白 {len(mas)} 本の中心  {distance(cn, cm):6.2f} dB")
    print(f"  語り手の中の広がり（{len(pairs(nar))} 組の中央値）       "
          f"{statistics.median(pairs(nar)):6.2f} dB")
    print(f"  真白 4 本の広がり（6 組の中央値）             {statistics.median(pairs(mas)):6.2f} dB")
    print(f"  真白 4 組の内訳 {[round(x, 2) for x in sorted(pairs(mas))]}")
    for k, ref in refs.items():
        own = [distance(ref, v) for v in env[k].values()]
        other = [distance(refs["mashiro" if k == "narrator" else "narrator"], v)
                 for v in env[k].values()]
        print(f"  {k:8s} 自分の参照まで {statistics.median(own):6.2f} dB / 相手の参照まで "
              f"{statistics.median(other):6.2f} dB")
    print(f"  参照どうし（語り手 ↔ 真白）                    "
          f"{distance(refs['narrator'], refs['mashiro']):6.2f} dB")


if __name__ == "__main__":
    main()
