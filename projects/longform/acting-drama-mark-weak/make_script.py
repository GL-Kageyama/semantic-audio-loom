#!/usr/bin/env python
"""`drama/script.yaml` から、強くない行（subtle / moderate）を 12 行選んで対を作る。

文末が「。」で、途中に「！」「？」「…」を持たない行だけ。微妙 6・中庸 6 を等間隔に抜く。
各 行 × 記号 2（`。` / `！`）× seed 1〜5 = 120 本。

  PYTHONPATH=. <venv>/bin/python projects/longform/acting-drama-mark-weak/make_script.py
"""
import os

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), "drama", "script.yaml")
FIELDS = ("character", "emotion", "intensity", "volume", "speed", "delivery")


def spread(xs, n):
    step = len(xs) / n
    return [xs[int(i * step)] for i in range(n)]


def main():
    cues = yaml.safe_load(open(SRC, encoding="utf-8"))["cues"]
    ok = [c for c in cues
          if c.get("intensity") in ("subtle", "moderate")
          and c["line"].rstrip().endswith("。")
          and not any(m in c["line"] for m in "！？…")]
    pick = (spread([c for c in ok if c["intensity"] == "subtle"], 6)
            + spread([c for c in ok if c["intensity"] == "moderate"], 6))

    out = []
    for c in pick:
        base = c["line"].rstrip()
        for seed in (1, 2, 3, 4, 5):
            for mark, suffix in (("。", "period"), ("！", "exclaim")):
                f = {k: c[k] for k in FIELDS if k in c}
                out.append(dict(f, line=base[:-1] + mark, seed=seed, beta=0.7,
                                name=f"dw-{c['name']}-{suffix}-s{seed}"))

    head = """# 作品の台詞のうち、強くない行に `！` を書いたら、声は動くか
#
# `drama/script.yaml` から intensity が subtle / moderate の行で、文末が「。」・
# 途中に「！」「？」「…」を持たないものを 12 行（微妙 6・中庸 6）選び、
# 文末だけ `！` にした対を seed 5 本で焼く（12 × 2 記号 × 5 seed = 120 本）。
# 強度の欄は台本のまま。作品と同じ beta 0.7。このファイルは make_script.py が作る。
"""
    body = yaml.safe_dump({"name": "acting-drama-mark-weak", "default_pause": 0.0,
                           "cues": out}, allow_unicode=True, sort_keys=False)
    open(os.path.join(HERE, "script.yaml"), "w", encoding="utf-8").write(head + body)
    print(len(out))


if __name__ == "__main__":
    main()
