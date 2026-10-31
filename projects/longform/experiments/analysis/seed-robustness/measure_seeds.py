#!/usr/bin/env python
"""床（beta 0.0）の演劇を seed 1〜3 で作り、作品の段の数が seed に依るかを測る。

  PYTHONPATH=. .venv/bin/python projects/longform/experiments/analysis/seed-robustness/measure_seeds.py

台詞・演技・間・効果音は同じで、cue の `seed` だけが違う。出力は seeds.tsv
（267 行＝89 キュー×3 版）。指標の定義は semantic_audio_loom/skills/act_probe.py。
"""
from __future__ import annotations

import csv
import os
import statistics
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))


def _lf_root(d=HERE):
    """projects/longform の根まで上へ辿る（REPORT.md と assets のある所）。"""
    while not os.path.exists(os.path.join(d, "REPORT.md")):
        d = os.path.dirname(d)
    return d

BASE = _lf_root()
ROOT = os.path.dirname(os.path.dirname(BASE))
sys.path.insert(0, ROOT)

from semantic_audio_loom.skills import act_probe  # noqa: E402

VERSIONS = {"1": "drama-beta00", "2": "drama-beta00-s2", "3": "drama-beta00-s3"}
METRICS = ("f0_median_hz", "f0_range_st", "rate_mora_s", "pause_ratio",
           "energy_median_db", "voiced_fraction")


def main() -> None:
    cues = yaml.safe_load(open(os.path.join(BASE, "drama-beta00", "script.yaml")))["cues"]
    rows = []
    for seed, work in VERSIONS.items():
        vdir = os.path.join(BASE, "assets", work, "voice")
        for c in cues:
            path = os.path.join(vdir, c["name"] + ".wav")
            if not os.path.exists(path):
                print(f"無し: {path}", file=sys.stderr)
                continue
            e = act_probe.measure(path)
            rows.append({
                "seed": seed, "name": c["name"], "character": c["character"],
                "emotion": c["emotion"], "duration": e["duration"],
                **{k: e[k] for k in METRICS},
            })
    out = os.path.join(HERE, "seeds.tsv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter="\t")
        w.writeheader()
        w.writerows(rows)
    print(f"{out}: {len(rows)} 行")

    print(f"{'seed':>4s} {'感情幅Hz':>8s} {'二人差Hz':>8s} {'抑揚st':>6s} {'間':>5s} {'声s':>6s}")
    for seed in VERSIONS:
        sub = [r for r in rows if r["seed"] == seed]
        eme = {}
        for r in sub:
            eme.setdefault(r["emotion"], []).append(float(r["f0_median_hz"]))
        eme = {e: statistics.mean(v) for e, v in eme.items()}
        res = {"mashiro": [], "niji": []}
        for r in sub:
            res[r["character"]].append(float(r["f0_median_hz"]) - eme[r["emotion"]])
        rng = {}
        for r in sub:
            rng.setdefault(r["emotion"], []).append(float(r["f0_range_st"]))
        print(f"{seed:>4s} {max(eme.values()) - min(eme.values()):8.1f}"
              f" {statistics.mean(res['mashiro']) - statistics.mean(res['niji']):+8.2f}"
              f" {statistics.mean([statistics.mean(v) for v in rng.values()]):6.2f}"
              f" {statistics.mean([float(r['pause_ratio']) for r in sub]):5.3f}"
              f" {sum(float(r['duration']) for r in sub):6.1f}")


if __name__ == "__main__":
    main()
