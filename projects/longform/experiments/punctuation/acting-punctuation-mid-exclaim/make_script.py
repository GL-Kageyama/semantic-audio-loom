#!/usr/bin/env python
"""文中の `！` は効くか —— 文末と途中で、記号の置き場所だけを替える。

`experiments/punctuation/acting-punctuation-period/` は「途中の句点」が文末の `！` を打ち消すことを測った
（+39.3 → +14.6 Hz）。ここでは途中に **`！`** を置くとどうなるかを見る。

台本の行 y06（ニジ・joy・18 文字・読点 2 つ）を使い、2 つ目の読点を記号に替える。

  base   黒くて、太ってて、こっちを見てた。   （台本のまま）
  end    黒くて、太ってて、こっちを見てた！   （文末だけ）
  mid    黒くて、太ってて！こっちを見てた。   （途中に `！`）
  midp   黒くて、太ってて。こっちを見てた。   （途中に `。`＝対照）
  both   黒くて、太ってて！こっちを見てた！   （途中と文末）

5 通り × seed 5 = 25 本。欄は台本のまま。

  PYTHONPATH=. <venv>/bin/python projects/longform/experiments/punctuation/acting-punctuation-mid-exclaim/make_script.py
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
FIELDS = ("character", "emotion", "intensity", "volume", "speed", "delivery", "beta")
LINES = {
    "base": "黒くて、太ってて、こっちを見てた。",
    "end": "黒くて、太ってて、こっちを見てた！",
    "mid": "黒くて、太ってて！こっちを見てた。",
    "midp": "黒くて、太ってて。こっちを見てた。",
    "both": "黒くて、太ってて！こっちを見てた！",
}


def main():
    cues = {c["name"]: c for c in yaml.safe_load(open(SRC, encoding="utf-8"))["cues"]}
    c = cues[NAME]
    out = []
    for key, line in LINES.items():
        f = {k: c[k] for k in FIELDS if k in c}
        for seed in (1, 2, 3, 4, 5):
            out.append(dict(f, line=line, pause_before=0.0, seed=seed,
                            name=f"pe-{key}-s{seed}"))
    head = """# 文中の `！`（台本の y06・5 通り × seed 5）
#
# base＝台本のまま／end＝文末だけ／mid＝途中に `！`／midp＝途中に `。`／both＝両方。
# `make_script.py` が作る。欄は台本のまま。
"""
    body = yaml.safe_dump({"name": "acting-punctuation-mid-exclaim", "default_pause": 0.0,
                           "cues": out}, allow_unicode=True, sort_keys=False)
    open(os.path.join(HERE, "script.yaml"), "w", encoding="utf-8").write(head + body)
    print(len(out), c["line"])


if __name__ == "__main__":
    main()
