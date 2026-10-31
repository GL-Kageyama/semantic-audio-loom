#!/usr/bin/env python
"""演劇の終わりの場面（s60〜s72）を、書かれたまま／文末だけ `！` の 2 通りで並べる。

`drama/script.yaml` の cue はそのまま（感情・強度・声量・速さ・delivery・seed・pause_before）。
変えるのは文末の `。` → `！` だけ。s67 はもとから `！` なので、そのまま。

  PYTHONPATH=. <venv>/bin/python projects/longform/drama-scene-mark/make_script.py
"""
import os

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), "drama", "script.yaml")
NAMES = [f"s{i}" for i in range(60, 73)]
FIELDS = ("character", "emotion", "intensity", "volume", "speed", "delivery",
          "pause_before", "seed", "beta")


def main():
    cues = {c["name"]: c for c in yaml.safe_load(open(SRC, encoding="utf-8"))["cues"]}
    out = []
    for tag in ("period", "exclaim"):
        for i, name in enumerate(NAMES):
            c = cues[name]
            line = c["line"]
            if tag == "exclaim" and line.endswith("。"):
                line = line[:-1] + "！"
            f = {k: c[k] for k in FIELDS if k in c}
            f.setdefault("pause_before", 0.0)
            if tag == "exclaim" and i == 0:
                f["pause_before"] = 2.0     # 前半との境目
            if tag == "period" and i == 0:
                f["pause_before"] = 0.2
            out.append(dict(f, line=line, name=f"{tag[0]}m-{name}"))

    head = """# 聞き比べ：場面まるごと、文末だけ `！` にしたらどうなるか
#
# 演劇の終わりの場面（s60〜s72・13 行）を、書かれたまま（前半）と
# 文末だけ `！` にした版（後半）で続けて並べる。欄も seed も pause も同じ。
# `make_script.py` が作る。
"""
    body = yaml.safe_dump({"name": "drama-scene-mark", "default_pause": 0.0, "cues": out},
                          allow_unicode=True, sort_keys=False)
    open(os.path.join(HERE, "script.yaml"), "w", encoding="utf-8").write(head + body)
    print(len(out))


if __name__ == "__main__":
    main()
