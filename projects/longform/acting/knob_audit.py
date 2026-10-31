"""作品が使った Direction の語を数える。

強度と声量は、語が 5 つ・4 つあっても、声を動かす段は少ない
（`projects/longform/experiments/intensity/acting-intensity/`・`projects/longform/experiments/delivery/acting-volume/`）。
台本がどの語にどれだけ座っているかを、人物ごとに数える。

「同じ段」は、Provider がプロンプトへ足す一言が同じ語の組で数える
（`semantic_audio_loom/providers/tsukasa.py` の `_INTENSITY_PHRASES` から導く。
一言が同じなら同じ声になる）。この組は、実際に聴こえる段の数とは別
（いまの表では 4 語それぞれに一言があり、残る段の数は anger・joy で 2、sadness で 3。
`projects/longform/experiments/intensity/acting-intensity-steps-new/`）。

使い方:
    PYTHONPATH=. <venv> projects/longform/acting/knob_audit.py
"""
from __future__ import annotations

import collections
import os
import sys

import yaml

from semantic_audio_loom.engine.resolve import INTENSITY_MAP
from semantic_audio_loom.providers.tsukasa import _intensity_phrase

HERE = os.path.abspath(__file__)
LONGFORM = os.path.dirname(os.path.dirname(HERE))
WORKS = ["explainer", "drama"]

INTENSITY_ORDER = list(INTENSITY_MAP)
VOLUME_ORDER = ["whisper", "quiet", "normal", "loud"]

# プロンプトに足される一言が同じ語 → 声が同じ。表を直せばこの組も動く。
_BY_PHRASE = collections.defaultdict(list)
for _word, _value in INTENSITY_MAP.items():
    _BY_PHRASE[_intensity_phrase(_value)].append(_word)
SAME_RUNG = {w for p, ws in _BY_PHRASE.items() if p and len(ws) > 1 for w in ws}
SAME_RUNG_LABEL = ("同じ段 (" + "+".join(sorted(SAME_RUNG, key=INTENSITY_ORDER.index)) + ")"
                   if SAME_RUNG else "同じ段 (なし)")


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
            same = sum(inten[w] for w in SAME_RUNG)
            above = inten["strong"] + inten["overwhelming"]
            print(f"  {ch:10s} n={n:3d}  強度: " + " ".join(
                f"{k}={inten[k]}" for k in INTENSITY_ORDER if inten[k]))
            print(f"  {'':10s}        声量: " + " ".join(
                f"{k}={vol[k]}" for k in VOLUME_ORDER if vol[k]))
            print(f"  {'':10s}        {SAME_RUNG_LABEL} {same}/{n} ({same/n:.0%})"
                  f"  strong 以上 {above}/{n} ({above/n:.0%})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
