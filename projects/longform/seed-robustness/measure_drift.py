#!/usr/bin/env python
"""作品の前半・中盤・後半で、二人の高さの差が動くかを見る。

  PYTHONPATH=. .venv/bin/python projects/longform/seed-robustness/measure_drift.py

キュー 1 本ずつは独立に生成されている（設定と seed が同じなら同じ音）。したがって
話の進み具合そのものが音を変えることはなく、三つの区間の差は**台本の設定の composition**
からしか出ない。ここではそれを確かめる。

- 床 0.0：seed 1〜3（seeds.tsv）
- 既定 0.7：seed 1（drama-level/levels.tsv）と seed 2（assets/drama-s2/voice、未生成なら測る）
"""
from __future__ import annotations

import csv
import glob
import os
import statistics
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
BASE = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(BASE))
sys.path.insert(0, ROOT)

from semantic_audio_loom.skills import act_probe  # noqa: E402


def load_f0() -> dict[str, dict[str, float]]:
    cues = yaml.safe_load(open(os.path.join(BASE, "drama", "script.yaml")))["cues"]
    order = [c["name"] for c in cues]
    maps: dict[str, dict[str, float]] = {}

    for r in csv.DictReader(open(os.path.join(HERE, "seeds.tsv")), delimiter="\t"):
        maps.setdefault(f"0.0 seed{r['seed']}", {})[r["name"]] = float(r["f0_median_hz"])
    levels = os.path.join(BASE, "drama-level", "levels.tsv")
    for r in csv.DictReader(open(levels), delimiter="\t"):
        if r["beta"] == "0.7":
            maps.setdefault("0.7 seed1", {})[r["name"]] = float(r["f0_median_hz"])
    s2dir = os.path.join(BASE, "assets", "drama-s2", "voice")
    if os.path.isdir(s2dir):
        maps["0.7 seed2"] = {
            os.path.basename(p)[:-4]: act_probe.measure(p)["f0_median_hz"]
            for p in glob.glob(os.path.join(s2dir, "*.wav"))
        }
    return {k: v for k, v in maps.items() if all(n in v for n in order)}


def main() -> None:
    cues = yaml.safe_load(open(os.path.join(BASE, "drama", "script.yaml")))["cues"]
    order = [c["name"] for c in cues]
    ch = {c["name"]: c["character"] for c in cues}
    emo = {c["name"]: c["emotion"] for c in cues}
    n = len(order)
    print(f"{'版':12s} {'前半':>7s} {'中盤':>7s} {'後半':>7s}   （真白 − ニジ・Hz・感情の平均を引いた残差）")
    for label, m in load_f0().items():
        em: dict[str, list[float]] = {}
        for x in order:
            em.setdefault(emo[x], []).append(m[x])
        em = {k: statistics.mean(v) for k, v in em.items()}
        resid = {x: m[x] - em[emo[x]] for x in order}
        cells = []
        for k in range(3):
            sub = order[k * n // 3:(k + 1) * n // 3]
            a = [resid[x] for x in sub if ch[x] == "mashiro"]
            b = [resid[x] for x in sub if ch[x] == "niji"]
            cells.append(statistics.mean(a) - statistics.mean(b))
        print(f"{label:12s} " + " ".join(f"{c:+7.1f}" for c in cells))


if __name__ == "__main__":
    main()
