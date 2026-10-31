#!/usr/bin/env python
"""同じ場面を 3 通りで並べる見本：台本のまま／強い 3 行だけ `！`／全部 `！`（seed 3）。

`experiments/scene/drama-scene-mark-seed/`（全部 `！`）と `experiments/scene/drama-scene-mark-selective/`（3 行）で
測った「置く行が増えるほど山は低くなる」を耳で確かめるための見本。
間（`pause_before`）は台本のまま、区切りに 2.0 秒を足す。

  PYTHONPATH=. <venv>/bin/python projects/longform/experiments/scene/drama-scene-mark-choice/make_script.py
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
SEED = 3
FIELDS = ("character", "emotion", "intensity", "volume", "speed", "delivery",
          "pause_before", "beta")
BLOCKS = (
    ("asis", "台本のまま。この場面に、感嘆符はひとつだけ。", set()),
    ("strong", "強い三行だけに、感嘆符を足します。", {"s61", "s63", "s65"}),
    ("all", "全部に足すと、どうなるか。", set(NAMES)),
)
NARRATOR = dict(character="narrator", line="", emotion="neutral", intensity="moderate",
                volume="normal", speed="natural", delivery="controlled", seed=4,
                beta=0.7, pause_before=1.4)


def main():
    cues = {c["name"]: c for c in yaml.safe_load(open(SRC, encoding="utf-8"))["cues"]}
    out = []
    for i, (tag, intro, marked) in enumerate(BLOCKS):
        gap = 0.2 if i == 0 else 2.0
        out.append(dict(NARRATOR, line=intro, pause_before=gap, name=f"n-{tag}"))
        for j, name in enumerate(NAMES):
            c = cues[name]
            line = c["line"]
            if name in marked and line.endswith("。"):
                line = line[:-1] + "！"
            f = {k: c[k] for k in FIELDS if k in c}
            f.setdefault("pause_before", 0.0)
            if j == 0:
                f["pause_before"] = max(f["pause_before"], 0.8)
            out.append(dict(f, line=line, seed=SEED, beta=f.get("beta", 0.7),
                            name=f"{tag}-{name}"))

    head = """# 見本：同じ場面を 3 通り（台本のまま／強い 3 行だけ `！`／全部 `！`・seed 3）
#
# `make_script.py` が `drama/script.yaml` から作る。欄と間は台本のまま。
"""
    body = yaml.safe_dump({"name": "drama-scene-mark-choice", "default_pause": 0.0,
                           "cues": out}, allow_unicode=True, sort_keys=False)
    open(os.path.join(HERE, "script.yaml"), "w", encoding="utf-8").write(head + body)
    print(len(out))


if __name__ == "__main__":
    main()
