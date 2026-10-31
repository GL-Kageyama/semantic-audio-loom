#!/usr/bin/env python
"""「選んで置く」を試す：強い 3 行だけに `！` を置いた場面と、書いたままの場面。

`experiments/scene/drama-scene-mark-seed/` で分かった「全部に置くと山場が消える」への答え。
`intensity: strong` の行（s61・s63・s65）だけを `！` にした版と、台本のままの版を
seed 1〜5 で焼く（13 行 × 条件 2 × seed 5 = 130 本）。

  PYTHONPATH=. <venv>/bin/python projects/longform/experiments/scene/drama-scene-mark-selective/make_script.py
"""
import os

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))


def _lf_root(d=HERE):
    """projects/longform の根まで上へ辿る（REPORT.md と assets のある所）。"""
    while not os.path.exists(os.path.join(d, "REPORT.md")):
        d = os.path.dirname(d)
    return d

SRC = os.path.join(_lf_root(), "drama", "script.yaml")
NAMES = [f"s{i}" for i in range(60, 73)]
FIELDS = ("character", "emotion", "intensity", "volume", "speed", "delivery", "beta")


def main():
    cues = {c["name"]: c for c in yaml.safe_load(open(SRC, encoding="utf-8"))["cues"]}
    marked = [n for n in NAMES if cues[n].get("intensity") == "strong"]
    out = []
    for cond in ("asis", "strong"):
        for name in NAMES:
            c = cues[name]
            line = c["line"]
            if cond == "strong" and name in marked and line.endswith("。"):
                line = line[:-1] + "！"
            f = {k: c[k] for k in FIELDS if k in c}
            for seed in (1, 2, 3, 4, 5):
                out.append(dict(f, line=line, pause_before=0.0, seed=seed,
                                name=f"{cond}-{name}-s{seed}"))

    head = """# 強い 3 行だけに `！` を置いた場面（`strong` 条件）と、台本のまま（`asis`）
#
# s61・s63・s65 が `intensity: strong`。ほかの行は「。」のまま。
# `make_script.py` が `drama/script.yaml` から作る。
"""
    body = yaml.safe_dump({"name": "drama-scene-mark-selective", "default_pause": 0.0,
                           "cues": out}, allow_unicode=True, sort_keys=False)
    open(os.path.join(HERE, "script.yaml"), "w", encoding="utf-8").write(head + body)
    print(len(out), marked)


if __name__ == "__main__":
    main()
