# 場面まるごと文末を `！` にしたら、声はどう動くか

`drama/script.yaml` の終わりの場面（s60〜s72・13 行）を、**台本のまま**と**文末の `。` を
`！` にしただけ**の 2 通りで焼き、続けて並べた（26 本）。感情・強度・声量・速さ・
`delivery`・seed・`pause_before` はすべて同じ。台本は [`make_script.py`](make_script.py) が作る。

## 結果（seed は台本のまま 1 本）

| 行 | 台本のまま | `！` | 差 |
| --- | --- | --- | --- |
| s60 niji joy | 320.4 Hz | 364.8 | **+44.4** |
| s61 mashiro sadness「……ずるい。」 | 305.9 | 337.5 | **+31.6** |
| s62 niji joy「ずるいね。」 | 283.8 | 326.9 | **+43.1** |
| s63 mashiro sadness「まだ、話したい。」 | 298.1 | 300.6 | +2.5 |
| s64 niji calm | 272.5 | 291.2 | +18.7 |
| s65 mashiro fear「ニジ。」 | 309.4 | 440.2 | **+130.8** |
| s66 niji joy | 323.2 | 370.1 | **+46.9** |
| s67 mashiro fear「ニジ！」 | 453.1 | 453.1 | 0（もとから `！`） |
| s68 mashiro anxiety「……もしもし。」 | 292.1 | 329.7 | **+37.6** |
| s69 mashiro loneliness「もしもし。」 | 285.4 | 355.5 | **+70.1** |
| s70 mashiro sadness「……ばか。」 | 329.7 | 測れず | — |
| s71 mashiro sadness | 307.7 | 368.0 | **+60.3** |
| s72 mashiro loneliness「おやすみ。」 | 305.9 | 349.4 | **+43.5** |

## 読み

- **測れた 11 行はすべて上がる**（+2.5〜+130.8・平均 **+48.1**）。
- **もとから `！` の s67 は動かない**（453.1 Hz・作品でいちばん高い行）。
  記号は「まだ無い行」に足すもの。
- **全部に `！` を書くと、山場が目立たなくなる**——ただし**1 seed では言えない**。
  ここ（seed 1）では s67 と 2 番目の差が 129.9 → 12.9 Hz に縮むが、seed 5 本で測った
  [`drama-scene-mark-seed/`](../drama-scene-mark-seed/) では **5 本中 4 本で s67 が
  ほかの行に抜かれる**（書いたままでは 5 本すべて 1 位）。**記号は選んで置く。**
  ⚠️ このディレクトリの差（+48.1）も seed 1 の値で、5 seed の平均は **+63.9**。
- ⚠️ seed は 1 本だけ（s63 の +2.5 は
  [`acting-drama-mark/`](../acting-drama-mark/) の seed 1〜3 の幅 +2.5〜+88.6 の下端）。行ごとの向きは
  [`acting-drama-mark-weak/`](../acting-drama-mark-weak/)（弱い 12 行 × seed 5）と
  [`acting-drama-mark/`](../acting-drama-mark/)（強い 9 行 × seed 3）で確かめてある。
- 見本：`examples/longform-drama-scene-mark/`（103.7 秒・−21.47 LUFS・LRA 12.40・**未達
  （音量・幅）**・声だけなので静か）。
