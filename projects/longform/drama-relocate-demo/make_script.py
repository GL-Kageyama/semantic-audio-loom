#!/usr/bin/env python
"""山を移す見本：台本のまま／s68 に足すだけ／s67 の `！` を戻して s68 に足す（seed 3）。

`drama-scene-mark-relocate/`（195 本）で測った「足すだけは 4/5・外してから足すと 5/5」を
耳で確かめるための見本。区切りの語り手 3 本を足し、区切りに 2.0 秒を空ける。

  PYTHONPATH=. <venv>/bin/python projects/longform/drama-relocate-demo/make_script.py
"""
import os

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(os.path.dirname(HERE), "drama", "script.yaml")
NAMES = [f"s{i}" for i in range(60, 73)]
SEED = 3
FIELDS = ("character", "emotion", "intensity", "volume", "speed", "delivery",
          "pause_before", "beta")
BLOCKS = (
    ("asis", "台本のまま。山の行に、感嘆符がひとつ。", False, False),
    ("keep", "しずくの行に、感嘆符を足します。", True, False),
    ("move", "足したうえで、もとの山の感嘆符を外します。", True, True),
)
NARRATOR = dict(character="narrator", line="", emotion="neutral", intensity="moderate",
                volume="normal", speed="natural", delivery="controlled", seed=4,
                beta=0.7)


def main():
    cues = {c["name"]: c for c in yaml.safe_load(open(SRC, encoding="utf-8"))["cues"]}
    out = []
    for i, (tag, intro, add, strip) in enumerate(BLOCKS):
        out.append(dict(NARRATOR, line=intro, name=f"n-{tag}",
                        pause_before=1.4 if i == 0 else 2.0))
        for j, name in enumerate(NAMES):
            c = cues[name]
            line = c["line"]
            if add and name == "s68" and line.endswith("。"):
                line = line[:-1] + "！"
            if strip and name == "s67" and line.endswith("！"):
                line = line[:-1] + "。"
            f = {k: c[k] for k in FIELDS if k in c}
            f.setdefault("pause_before", 0.0)
            if j == 0:
                f["pause_before"] = max(f["pause_before"], 0.8)
            out.append(dict(f, line=line, seed=SEED, beta=f.get("beta", 0.7),
                            name=f"{tag}-{name}"))

    head = """# 見本：山を移す（台本のまま／s68 に足す／s67 を戻して s68 に足す・seed 3）
#
# `make_script.py` が `drama/script.yaml` から作る。欄と間は台本のまま。
"""
    body = yaml.safe_dump({"name": "drama-relocate-demo", "default_pause": 0.0,
                           "cues": out}, allow_unicode=True, sort_keys=False)
    open(os.path.join(HERE, "script.yaml"), "w", encoding="utf-8").write(head + body)
    print(len(out))


if __name__ == "__main__":
    main()
