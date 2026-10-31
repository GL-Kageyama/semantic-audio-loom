#!/usr/bin/env python
"""文中の `！` を耳で確かめる見本：同じ行の記号だけを 5 通りに（seed 3）。

台本の y06（ニジ・joy・18 文字）で、2 つ目の読点を記号に替える。
区切りの語り手を入れて、5 通りを続けて聴けるようにする。

  PYTHONPATH=. <venv>/bin/python projects/longform/experiments/demos/mid-mark-demo/make_script.py
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
NAME = "y06"
SEED = 3
FIELDS = ("character", "emotion", "intensity", "volume", "speed", "delivery",
          "pause_before", "beta")
VARIANTS = (
    ("base", "台本のまま。", "黒くて、太ってて、こっちを見てた。"),
    ("end", "文末だけ、感嘆符。", "黒くて、太ってて、こっちを見てた！"),
    ("mid", "途中だけ、感嘆符。", "黒くて、太ってて！こっちを見てた。"),
    ("midp", "途中を、句点に。", "黒くて、太ってて。こっちを見てた。"),
    ("both", "両方に、感嘆符。", "黒くて、太ってて！こっちを見てた！"),
)
NARRATOR = dict(character="narrator", emotion="neutral", intensity="moderate",
                volume="normal", speed="natural", delivery="controlled", seed=4, beta=0.7)


def main():
    c = {x["name"]: x for x in yaml.safe_load(open(SRC, encoding="utf-8"))["cues"]}[NAME]
    f = {k: c[k] for k in FIELDS if k in c}
    f.setdefault("pause_before", 0.0)
    out = []
    for i, (tag, intro, line) in enumerate(VARIANTS):
        out.append(dict(NARRATOR, line=intro, name=f"n-{tag}",
                        pause_before=1.4 if i == 0 else 1.2))
        out.append(dict(f, line=line, seed=SEED, beta=f.get("beta", 0.7),
                        name=f"{tag}-line", pause_before=0.3))

    head = """# 見本：文中の `！`（台本の y06・5 通り・seed 3）
#
# `make_script.py` が `drama/script.yaml` から作る。欄は台本のまま。
"""
    body = yaml.safe_dump({"name": "mid-mark-demo", "default_pause": 0.0,
                           "cues": out}, allow_unicode=True, sort_keys=False)
    open(os.path.join(HERE, "script.yaml"), "w", encoding="utf-8").write(head + body)
    print(len(out))


if __name__ == "__main__":
    main()
