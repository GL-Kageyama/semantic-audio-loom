# 山を移せるのは s68 だけか —— 別の行に替えても、同じように移る

`experiments/scene/drama-scene-mark-relocate/` は s68 へ移した。ここでは**狙う行を s60・s66 に替えて**
同じことをした（13 行 × 3 通り × seed 5 × 狙い 2 行 = **390 本**）。欄・間は台本のまま。

- `<target>-asis` … 台本のまま（s67 の `！` はそのまま）
- `<target>-keep` … 狙う行にだけ `！` を足す
- `<target>-move` … 狙う行に足し、**s67 の `！` を `。` に戻す**

## 狙う行が 1 位になるか（13 行のうち）

| 狙い | 通り | 狙う行の f0 | 順位（seed 1〜5） | 次点との差の平均 |
| --- | --- | --- | --- | --- |
| s60（joy・9 文字） | `asis` | 303.7 Hz | 4・3・5・5・3 | −87.2 |
| | `keep` | 371.1 | 2・**1**・2・2・**1** | −19.9 |
| | `move` | 371.1 | **1・1・1・1・1** | **+47.0** |
| s66（joy・10 文字） | `asis` | 314.7 | 3・1・2・6・6 | −76.3 |
| | `keep` | 353.5 | 2・**1**・2・2・2 | −37.5 |
| | `move` | 353.5 | **1・1・1・1・1** | **+38.6** |

- **足すだけでは足りない**：s60 は 2/5・s66 は 1/5 でしか 1 位にならない（s67 が
  453.1 Hz のまま残るため）。s68 のときは 4/5 だった（あの行の伸びが大きかった）。
- **外してから足すと、3 つの狙いすべてで 5/5**（s60 +47.0・s66 +38.6・s68 +88.1 Hz）。
  **山を移すのは「狙う行を上げる」より「もとの山を下げる」ほうが効く。**
- 動くのは狙った行と s67 だけ。ほかの 11 行は同じ seed なら同値。

## 測った値・出典

- 1 本ごとの値は [`probe.tsv`](probe.tsv)（`bin/act_probe.py --tsv`）。同期の検査は
  390/390 一致（`check_script_sync.py --dir experiments/scene/drama-scene-mark-relocate2`）。
- 台本：`drama/script.yaml`（この実験は台本を書き換えていない）。
- 前の段：[`experiments/scene/drama-scene-mark-relocate/`](../drama-scene-mark-relocate)（s68 へ移す・195 本）・
  [`experiments/scene/drama-scene-mark-selective/`](../drama-scene-mark-selective)（3 行だけ `！`）・
  [`experiments/scene/drama-scene-mark-seed/`](../drama-scene-mark-seed)（全部 `！`）
