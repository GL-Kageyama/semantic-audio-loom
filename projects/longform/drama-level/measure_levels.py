#!/usr/bin/env python
"""演劇の三つの版（beta 0.7 / 0.3 / 0.0）を、キューごとに演技の指標で測る。

  PYTHONPATH=. .venv/bin/python projects/longform/drama-level/measure_levels.py

台詞・seed・間は三つとも同じなので、差は混ぜ方（beta）だけになる。
出力は levels.tsv（267 行＝89 キュー×3 版）。指標の定義は
semantic_audio_loom/skills/act_probe.py の冒頭にある。
"""
from __future__ import annotations

import csv
import os
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, ROOT)

from semantic_audio_loom.skills import act_probe  # noqa: E402

BASE = os.path.dirname(HERE)
VERSIONS = {"0.7": "drama", "0.3": "drama-beta03", "0.0": "drama-beta00"}
METRICS = ("f0_median_hz", "f0_range_st", "rate_mora_s", "pause_ratio",
           "energy_median_db", "voiced_fraction")


def main() -> None:
    cues = yaml.safe_load(open(os.path.join(BASE, "drama", "script.yaml")))["cues"]
    rows = []
    for beta, work in VERSIONS.items():
        vdir = os.path.join(BASE, "assets", work, "voice")
        for c in cues:
            path = os.path.join(vdir, c["name"] + ".wav")
            if not os.path.exists(path):
                print(f"無し: {path}", file=sys.stderr)
                continue
            e = act_probe.measure(path)
            rows.append({
                "beta": beta, "name": c["name"], "character": c["character"],
                "emotion": c["emotion"], "intensity": c["intensity"],
                "volume": c["volume"], "speed": c["speed"], "delivery": c["delivery"],
                "duration": e["duration"], **{k: e[k] for k in METRICS},
            })
    out = os.path.join(HERE, "levels.tsv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter="\t")
        w.writeheader()
        w.writerows(rows)
    print(f"{out}: {len(rows)} 行")


if __name__ == "__main__":
    main()
