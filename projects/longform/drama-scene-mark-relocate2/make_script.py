#!/usr/bin/env python
"""山を移せるのは s68 だけか —— 別の行（s60・s66）へ移しても、同じように移るか。

`drama-scene-mark-relocate/` は s68 へ移した。ここでは**狙う行を替えて**同じことをする
（13 行 × 3 通り × seed 5 × 狙い 2 行 = **390 本**）。

  <target>-asis … 台本のまま（s67 の `！` はそのまま）
  <target>-keep … 狙う行にだけ `！` を足す
  <target>-move … 狙う行に足し、s67 の `！` を `。` に戻す

  PYTHONPATH=. <venv>/bin/python projects/longform/drama-scene-mark-relocate2/make_script.py
"""
import os

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), "drama", "script.yaml")
NAMES = [f"s{i}" for i in range(60, 73)]
TARGETS = ("s60", "s66")
FIELDS = ("character", "emotion", "intensity", "volume", "speed", "delivery", "beta")


def main():
    cues = {c["name"]: c for c in yaml.safe_load(open(SRC, encoding="utf-8"))["cues"]}
    out = []
    for target in TARGETS:
        for cond in ("asis", "keep", "move"):
            for name in NAMES:
                c = cues[name]
                line = c["line"]
                if cond in ("keep", "move") and name == target and line.endswith("。"):
                    line = line[:-1] + "！"
                if cond == "move" and name == "s67" and line.endswith("！"):
                    line = line[:-1] + "。"
                f = {k: c[k] for k in FIELDS if k in c}
                for seed in (1, 2, 3, 4, 5):
                    out.append(dict(f, line=line, pause_before=0.0, seed=seed,
                                    name=f"{target}-{cond}-{name}-s{seed}"))

    head = """# 山を移せるのは s68 だけか（狙う行を s60・s66 に替える・390 本）
#
# `<target>-asis`／`-keep`（狙う行にだけ `！`）／`-move`（s67 の `！` も戻す）。
# `make_script.py` が `drama/script.yaml` から作る。
"""
    body = yaml.safe_dump({"name": "drama-scene-mark-relocate2", "default_pause": 0.0,
                           "cues": out}, allow_unicode=True, sort_keys=False)
    open(os.path.join(HERE, "script.yaml"), "w", encoding="utf-8").write(head + body)
    print(len(out))


if __name__ == "__main__":
    main()
