# `！` をどこに置くか —— 同じ場面を 3 通り並べる

`drama/script.yaml` の終わりの場面（s60〜s72・13 行）を、**台本のまま**・**`intensity:
strong` の 3 行（s61・s63・s65）だけ `！`**・**13 行すべて `！`** の 3 通りで続けて焼いた
（seed 3・**42 本**＋区切りの語り手 3 本）。欄・間は台本のまま、変えるのは文末の 1 字だけ。
台本は [`make_script.py`](make_script.py) が作る。耳で聴く見本は
[`examples/longform-drama-scene-choice/`](../../examples/longform-drama-scene-choice/)。

## 山場（s67）と次点の差

s67 は「ニジ！」で、この場面で唯一もとから `！` の行（どの条件でも 453.1 Hz・同じ音）。

| 条件 | s67 | 次点 | 差 | s67 の順位 |
| --- | --- | --- | --- | --- |
| 台本のまま（0 行に `！`） | 453.1 Hz | s66 326.0 | **+127.1** | 1 位 |
| 強い 3 行だけ `！` | 453.1 | s65 430.1 | **+23.0** | 1 位 |
| 全部 `！`（12 行に足す） | 453.1 | **s68 463.7** | **−10.6** | **2 位** |

- **置く行が増えるほど、山は低くなる**。s67 の高さは 3 通りとも同じ（同じ行・同じ seed）
  なのに、ほかの行が `！` を得た瞬間に追いつかれる。seed 5 本の平均の差は
  0 行 68.0 → 3 行 1.0 → 12 行 −43.3 Hz（[`drama-scene-mark-seed/`](../drama-scene-mark-seed/)・
  [`drama-scene-mark-selective/`](../drama-scene-mark-selective/)）。
- 3 行版で上がるのは、置いた行だけ（s61 272.5 → 353.4・s63 270.2 → 357.5・
  s65 257.2 → 430.1）。**ほかの 10 行は 1 Hz も動かない**（全 130 本で確認済み）。

## 測った値

- 173.2 秒・**−20.76 LUFS**・TP −1.00 dBTP・LRA 11.70 → **未達（音量）**（`--gain -0.40`）。
  声だけで長い間を含むため、ほかの見本より静か。ピークは既に天井で、直線のゲインでは
  上がらない（圧縮は掛けていない）。
- 1 本ごとの値は [`probe.tsv`](probe.tsv)（`bin/act_probe.py --tsv`）。

## 出典

- 台本：`drama/script.yaml`（この実験は台本を書き換えていない）
- 焼き直し：`projects/longform/explainer/build_voice.py --dir drama-scene-mark-choice`
- 組む・配る：`assemble.py --dir drama-scene-mark-choice`・`deliver.py`・`check_loudness.py`
