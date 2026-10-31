#!/usr/bin/env python
"""終わりの場面 13 行を、台本のまま／文末だけ `！` の対で seed 1〜5 焼く（130 本）。

`experiments/scene/drama-scene-mark/`（見本）は seed 1 本だけなので、向きと「山場の差」が seed で
動かないかをここで確かめる。欄・pause は台本のまま、変えるのは文末の 1 字だけ。

  PYTHONPATH=. <venv>/bin/python projects/longform/experiments/scene/drama-scene-mark-seed/make_script.py
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
FIELDS = ("character", "emotion", "intensity", "volume", "speed", "delivery",
          "pause_before", "beta")


def main():
    cues = {c["name"]: c for c in yaml.safe_load(open(SRC, encoding="utf-8"))["cues"]}
    out = []
    for name in NAMES:
        c = cues[name]
        for seed in (1, 2, 3, 4, 5):
            for tag, mark in (("period", "。"), ("exclaim", "！")):
                line = c["line"]
                if line.endswith("。"):
                    line = line[:-1] + mark
                f = {k: c[k] for k in FIELDS if k in c}
                f["pause_before"] = 0.0          # 測るため。見本は experiments/scene/drama-scene-mark/
                out.append(dict(f, line=line, seed=seed, name=f"{name}-{tag}-s{seed}"))

    head = """# 終わりの場面 13 行 × 記号 2 × seed 5（測るため。間は 0）
#
# `make_script.py` が `drama/script.yaml` から作る。文末の 1 字だけを変える。
"""
    body = yaml.safe_dump({"name": "drama-scene-mark-seed", "default_pause": 0.0,
                           "cues": out}, allow_unicode=True, sort_keys=False)
    open(os.path.join(HERE, "script.yaml"), "w", encoding="utf-8").write(head + body)
    print(len(out))


if __name__ == "__main__":
    main()
