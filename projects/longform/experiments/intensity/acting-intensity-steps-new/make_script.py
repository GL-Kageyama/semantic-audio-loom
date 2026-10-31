#!/usr/bin/env python
"""真ん中に文言が入った後、段はいくつになったか（subtle / moderate / strong × 3 感情 × seed 5）。

`experiments/basics/acting-matrix/` の `in-<感情>-subtle-s*`・`in-<感情>-strong-s*` と同じ設定・同じ seed。
subtle と strong の散文は変えていないので、**同じ音が返るはず**（md5 で確かめる）。
変わるのは moderate だけ。

  PYTHONPATH=. <venv>/bin/python projects/longform/experiments/intensity/acting-intensity-steps-new/make_script.py
"""
import os

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))


def _lf_root(d=HERE):
    """projects/longform の根まで上へ辿る（REPORT.md と assets のある所）。"""
    while not os.path.exists(os.path.join(d, "REPORT.md")):
        d = os.path.dirname(d)
    return d

SRC = os.path.join(_lf_root(), "experiments", "basics", "acting-matrix", "script.yaml")
EMOTIONS = ("anger", "joy", "sadness")
LEVELS = ("subtle", "moderate", "strong")
FIELDS = ("character", "line", "emotion", "volume", "speed", "delivery", "breathiness", "seed")


def main():
    cues = {(c["emotion"], c["intensity"], c["seed"]): c
            for c in yaml.safe_load(open(SRC, encoding="utf-8"))["cues"]}
    out = []
    for emo in EMOTIONS:
        for level in LEVELS:
            for seed in (1, 2, 3, 4, 5):
                c = cues[(emo, level, seed)]
                f = {k: c[k] for k in FIELDS}
                out.append(dict(f, intensity=level, pause_before=0.0,
                                name=f"new-{emo}-{level}-s{seed}"))
    head = """# 真ん中の文言を入れた後の 3 段（45 本）
#
# 設定・seed は experiments/basics/acting-matrix/ の in-<感情>-<段>-s* と同一。subtle と strong は
# 散文が変わっていないので同じ音が返る（md5 で確認）。変わるのは moderate だけ。
# `make_script.py` が experiments/basics/acting-matrix/script.yaml から作る。
"""
    body = yaml.safe_dump({"name": "acting-intensity-steps-new", "default_pause": 0.0,
                           "cues": out}, allow_unicode=True, sort_keys=False)
    open(os.path.join(HERE, "script.yaml"), "w", encoding="utf-8").write(head + body)
    print(len(out))


if __name__ == "__main__":
    main()
