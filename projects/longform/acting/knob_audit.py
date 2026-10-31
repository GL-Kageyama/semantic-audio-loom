"""作品が使った Direction の語を数える。

強度と声量は、語が 5 つ・4 つあっても、声を動かす段は少ない
（`projects/longform/acting-intensity/`・`projects/longform/acting-volume/`）。
台本がどの語にどれだけ座っているかを、人物ごとに数える。

使い方:
    PYTHONPATH=. <venv> projects/longform/acting/knob_audit.py
"""
from __future__ import annotations

import collections
import os
import sys

import yaml

HERE = os.path.abspath(__file__)
LONGFORM = os.path.dirname(os.path.dirname(HERE))
WORKS = ["explainer", "drama"]

# 声を動かす段（実測）。subtle と moderate は同じ段に数える。
INTENSITY_ORDER = ["none", "subtle", "moderate", "strong", "overwhelming"]
SAME_RUNG = {"none", "moderate"}          # プロンプトに足される一言が同じ
VOLUME_ORDER = ["whisper", "quiet", "normal", "loud"]


def load(work: str) -> list[dict]:
    path = os.path.join(LONGFORM, work, "script.yaml")
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["cues"]


def main() -> int:
    for work in WORKS:
        cues = load(work)
        by_char: dict[str, list[dict]] = collections.defaultdict(list)
        for c in cues:
            by_char[c.get("character", "?")].append(c)
        print(f"== {work}  {len(cues)} 本")
        for ch, cs in by_char.items():
            n = len(cs)
            inten = collections.Counter(c.get("intensity") for c in cs)
            vol = collections.Counter(c.get("volume") for c in cs)
            same = inten["subtle"] + inten["moderate"]
            above = inten["strong"] + inten["overwhelming"]
            print(f"  {ch:10s} n={n:3d}  強度: " + " ".join(
                f"{k}={inten[k]}" for k in INTENSITY_ORDER if inten[k]))
            print(f"  {'':10s}        声量: " + " ".join(
                f"{k}={vol[k]}" for k in VOLUME_ORDER if vol[k]))
            print(f"  {'':10s}        同じ段 (subtle+moderate) {same}/{n} ({same/n:.0%})"
                  f"  strong 以上 {above}/{n} ({above/n:.0%})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
