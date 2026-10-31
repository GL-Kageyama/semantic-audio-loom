#!/usr/bin/env python
"""床（beta 0.0）と、床＋pitch（真白 very_low / ニジ high）の 89 キューを測る。

  PYTHONPATH=. .venv/bin/python projects/longform/drama-beta00-pitch/measure_pitch.py

台詞・seed・間・beta は二つで同じなので、差は `pitch` の 2 語だけになる。
出力は probe.tsv（178 行＝89 キュー×2 版）。指標の定義は
semantic_audio_loom/skills/act_probe.py の冒頭にある。
"""
from __future__ import annotations

import csv
import os
import statistics
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))
sys.path.insert(0, ROOT)

from semantic_audio_loom.skills import act_probe  # noqa: E402

BASE = os.path.dirname(HERE)
VERSIONS = {"beta00": "drama-beta00", "beta00-pitch": "drama-beta00-pitch"}
METRICS = ("f0_median_hz", "f0_range_st", "rate_mora_s", "pause_ratio",
           "energy_median_db", "voiced_fraction")


def main() -> None:
    cues = yaml.safe_load(open(os.path.join(HERE, "script.yaml")))["cues"]
    rows = []
    for label, work in VERSIONS.items():
        vdir = os.path.join(BASE, "assets", work, "voice")
        for c in cues:
            path = os.path.join(vdir, c["name"] + ".wav")
            if not os.path.exists(path):
                print(f"無し: {path}", file=sys.stderr)
                continue
            e = act_probe.measure(path)
            rows.append({
                "version": label, "name": c["name"], "character": c["character"],
                "emotion": c["emotion"], "pitch": c.get("pitch", "natural"),
                "duration": e["duration"], **{k: e[k] for k in METRICS},
            })
    out = os.path.join(HERE, "probe.tsv")
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), delimiter="\t")
        w.writeheader()
        w.writerows(rows)
    print(f"{out}: {len(rows)} 行")

    # まとめ：人物の声の合計と、感情の偏りを除いた二人の差。
    for label in VERSIONS:
        sub = [r for r in rows if r["version"] == label]
        for ch in ("mashiro", "niji"):
            v = [float(r["duration"]) for r in sub if r["character"] == ch]
            f = [float(r["f0_median_hz"]) for r in sub if r["character"] == ch]
            print(f"{label:12s} {ch:8s} 声 {sum(v):6.1f} 秒  f0 中央値 {statistics.median(f):6.1f} Hz")
        emean = {}
        for r in sub:
            emean.setdefault(r["emotion"], []).append(float(r["f0_median_hz"]))
        emean = {e: statistics.mean(v) for e, v in emean.items()}
        resid = {"mashiro": [], "niji": []}
        for r in sub:
            resid[r["character"]].append(float(r["f0_median_hz"]) - emean[r["emotion"]])
        print(f"{label:12s} 感情の偏りを除いた差（真白 − ニジ）"
              f" {statistics.mean(resid['mashiro']) - statistics.mean(resid['niji']):+6.2f} Hz"
              f" / 感情 8 種の平均 f0 の幅 {max(emean.values()) - min(emean.values()):5.1f} Hz")


if __name__ == "__main__":
    main()
