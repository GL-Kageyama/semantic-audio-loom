#!/usr/bin/env python
"""山は「動かせる」か：`！` を別の行へ移すと、いちばん高い行は移るか。

`experiments/scene/drama-scene-mark/` 系で分かったのは「置く行が増えると山が消える」まで。
ここでは逆向きを見る——**`！` を 1 行に絞って移せば、山も移せるか**。

`s68`（「……もしもし」・全部 `！` の版で s67 を追い越した行）を狙う。3 通り × 13 行 × seed 5。

  asis … 台本のまま（s67 だけが `！`）
  keep … s68 にだけ `！` を足す（s67 の `！` はそのまま）
  move … s68 に足し、s67 の `！` を `。` に戻す（山を移す）

  PYTHONPATH=. <venv>/bin/python projects/longform/experiments/scene/drama-scene-mark-relocate/make_script.py
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
TARGET = "s68"


def main():
    cues = {c["name"]: c for c in yaml.safe_load(open(SRC, encoding="utf-8"))["cues"]}
    out = []
    for cond in ("asis", "keep", "move"):
        for name in NAMES:
            c = cues[name]
            line = c["line"]
            if cond in ("keep", "move") and name == TARGET and line.endswith("。"):
                line = line[:-1] + "！"
            if cond == "move" and name == "s67" and line.endswith("！"):
                line = line[:-1] + "。"
            f = {k: c[k] for k in FIELDS if k in c}
            for seed in (1, 2, 3, 4, 5):
                out.append(dict(f, line=line, pause_before=0.0, seed=seed,
                                name=f"{cond}-{name}-s{seed}"))

    head = """# 山を動かせるか：`！` を s68 へ移す（3 通り × 13 行 × seed 5）
#
# asis＝台本のまま／keep＝s68 にだけ足す／move＝s68 に足し s67 を「。」に戻す。
# `make_script.py` が `drama/script.yaml` から作る。
"""
    body = yaml.safe_dump({"name": "drama-scene-mark-relocate", "default_pause": 0.0,
                           "cues": out}, allow_unicode=True, sort_keys=False)
    open(os.path.join(HERE, "script.yaml"), "w", encoding="utf-8").write(head + body)
    print(len(out))


if __name__ == "__main__":
    main()
