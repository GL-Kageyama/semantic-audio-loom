# 出荷した表で、真ん中の帯を作り直す —— 測った音と 1 バイトも違わないか

`_INTENSITY_PHRASES` の真ん中の帯（0.40〜0.70）は空だった。そこへ
`"the feeling is moderately strong"` を入れて既定にした（`semantic_audio_loom/providers/tsukasa.py`）。
この実験は、**その既定の表で** `acting-mod-phrase/` と同じ 15 本を作り直し、
測ったときの音と突き合わせる（15 本・seed 1〜5 × anger / joy / sadness・beta 0.7）。

差し替えも小細工もしていない。`build_voice.py` をそのまま走らせただけ。

## 結果

| 突き合わせ | 値 |
| --- | --- |
| `acting-mod-phrase/` の 15 本との md5 | **15/15 一致**（1 バイトも違わない） |
| 文言なしの `acting-matrix/` との f0 差（anger） | **+1.3 Hz**（4/5）＝測ったときと同じ |
| 同上（joy） | **+1.7 Hz**（4/5） |
| 同上（sadness） | **+9.4 Hz**（5/5）＝測ったときと同じ |

**測った道と出荷した道は同じ音を出す。** `acting-mod-phrase/` の数字
（ sadness +9.4 Hz・5/5）は、そのまま既定の効きとして読める。

## 変えたのは真ん中だけ

| intensity | 文言 | 前 |
| --- | --- | --- |
| 〜0.40 | the feeling is faint, barely showing | 同じ |
| 0.41〜0.70 | **the feeling is moderately strong** | （空＝何も言わない） |
| 0.71〜0.90 | the feeling is strong, close to the surface | 同じ |
| 0.91〜 | the feeling is overwhelming, at its limit | 同じ |

`intensity: none`（0.0）が文言を足さないことも変わっていない。

## 気をつけること

- **moderate の台詞は、前と後で同じ seed でも別の音になる。** 散文が変われば音も変わる。
  いまの 2 作品で moderate なのは **explainer 32 行・drama 28 行**（全 137 行のうち 60 行）。
  焼き上がった `assets/` は前の音のまま残してあるので、**`--force` で作り直すとこの 60 行が変わる**
  （尺・f0・音量の検査も取り直しになる）。作り直すかは著者の裁定。
- 実験用の `acting-mod-phrase/` は、差し替え（`acting/mod_phrase_build.py`）を使わなくても
  同じ音が出るようになった。あの道具は残してある（帯を別の文言にしたときの対照用）。

## 測った値・出典

- 1 本ごとの値は [`probe.tsv`](probe.tsv)（`bin/act_probe.py --tsv`）。同期 15/15。
- 台本：[`script.yaml`](script.yaml)（`acting-mod-phrase/script.yaml` と欄・seed が同一）。
- 生成：`explainer/build_voice.py --dir acting-mod-phrase-ship`・15 本・22.2 秒・M2Pro-16GB・
  tsukasa（`timings.tsv`）。
- 元の測定：[`acting-mod-phrase/`](../acting-mod-phrase/)・
  [`acting-intensity/`](../acting-intensity/)（5 語 × 3 段）。
