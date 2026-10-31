#!/usr/bin/env python
"""解説の語りでも `！` は効くか —— 作品の 6 行で、文末だけ替える。

これまでの記号の測定は芝居（真白・ニジ）ばかりで、語り手は 1 行しか見ていない
（「ここが、大事です」+58.1）。ここでは**解説の本物の語り** 6 行で、`。`／`！` を
対にして seed 5 本ずつ焼く（6 行 × 2 × 5 = **60 本**）。

途中に `。` の無い行だけを選ぶ（途中の句点は効きを打ち消すため、対の見通しが濁る）。

  PYTHONPATH=. <venv>/bin/python projects/longform/experiments/punctuation/acting-explainer-mark/make_script.py
"""
import os

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))


def _lf_root(d=HERE):
    """projects/longform の根まで上へ辿る（REPORT.md と assets のある所）。"""
    while not os.path.exists(os.path.join(d, "REPORT.md")):
        d = os.path.dirname(d)
    return d

SRC = os.path.join(_lf_root(), "explainer", "script.yaml")
NAMES = ("n01", "n23", "n26", "c01", "x03", "n28")   # 15・17・21・25・33・38 文字
FIELDS = ("character", "emotion", "intensity", "volume", "speed", "delivery", "beta")


def main():
    cues = {c["name"]: c for c in yaml.safe_load(open(SRC, encoding="utf-8"))["cues"]}
    out = []
    for name in NAMES:
        c = cues[name]
        line = c["line"]
        assert line.endswith("。") and line.count("。") == 1, (name, line)
        for mark, tag in (("。", "period"), ("！", "exclaim")):
            f = {k: c[k] for k in FIELDS if k in c}
            for seed in (1, 2, 3, 4, 5):
                out.append(dict(f, line=line[:-1] + mark, pause_before=0.0, seed=seed,
                                name=f"ex-{name}-{tag}-s{seed}"))
    head = """# 解説の語りに `！`（作品の 6 行 × 記号 2 × seed 5）
#
# `make_script.py` が `explainer/script.yaml` から作る。欄は台本のまま、変えるのは文末 1 字。
"""
    body = yaml.safe_dump({"name": "acting-explainer-mark", "default_pause": 0.0,
                           "cues": out}, allow_unicode=True, sort_keys=False)
    open(os.path.join(HERE, "script.yaml"), "w", encoding="utf-8").write(head + body)
    print(len(out))


if __name__ == "__main__":
    main()
