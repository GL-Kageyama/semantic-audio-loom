# 真ん中に文言が入った後、段はいくつになったか

`_INTENSITY_PHRASES` の真ん中（0.41〜0.70）に `"the feeling is moderately strong"` を
入れた後の 3 段を、`acting-matrix/` と同じ設定・同じ seed で測り直した
（subtle / moderate / strong × anger / joy / sadness × seed 5 = **45 本**・beta 0.7・
台詞「明日、また来るね。」・mashiro）。

## 変えていない段は、同じ音

| 段 | md5 が `acting-matrix/` と一致 |
| --- | --- |
| subtle（30 本のうち） | **15/15** |
| strong（30 本のうち） | **15/15** |

**散文を変えていない段は、1 バイトも変わらない。** 変わったのは moderate の 15 本だけ。

## 段の間（同じ seed の対の差の平均）

| 段の間 | anger | joy | sadness |
| --- | --- | --- | --- |
| subtle → moderate | −1.3 Hz（1/5・p = 0.17） | **+2.1 Hz（5/5・p = 0.019）** | **+8.6 Hz（5/5・p = 0.0001）** |
| moderate → strong | **+8.7 Hz（5/5・p = 0.0017）** | **+7.2 Hz（5/5・p = 0.022）** | **+8.9 Hz（5/5・p = 0.0002）** |

帯が空だったとき（`acting-intensity/`）との違い：

| 段の間 | anger | joy | sadness |
| --- | --- | --- | --- |
| subtle → moderate（前） | −2.7（0/5） | +0.4（1/5） | −0.8（1/5） |
| subtle → moderate（後） | −1.3（1/5） | **+2.1（5/5）** | **+8.6（5/5）** |
| moderate → strong（前） | +10.0（5/5） | +8.8（5/5） | +18.3（5/5） |
| moderate → strong（後） | +8.7（5/5） | +7.2（5/5） | **+8.9（5/5）** |

- **sadness は 3 段になった。** 真ん中が上へ動いたぶん、subtle→moderate が +8.6 Hz に
  開き、moderate→strong は +18.3 → +8.9 Hz に縮んだ。**3 つの段が 8〜9 Hz で等間隔**。
- **anger は 2 段のまま。** 真ん中は動かない（−1.3 Hz・1/5）。
- **joy は真ん中がわずかに開いた**（+2.1 Hz・5/5・p = 0.019）。ただし **2 Hz は
  seed の振れ（84.6 Hz）の前では段として聴こえる大きさではない**——符号はそろったが、
  幅は anger・sadness の 1/4。
- **moderate → strong は 3 感情とも残る**（+7.2〜+8.9 Hz・すべて 5/5）。
  **一番大きい段は、どの感情でも「強」への一歩。**

## 気をつけること

- 測ったのは 1 行・1 人物・3 感情・beta 0.7。**ほかの行・ほかの感情では段の幅は変わりうる**
  （`acting-intensity-line2/` では跳ね幅が seed に強く依った）。
- moderate の台詞は、変更の前後で**同じ seed でも別の音**になる。2 作品で 60 行
  （explainer 32・drama 28）。焼き上がりは前の音のまま
  （[`acting-mod-phrase-ship/`](../acting-mod-phrase-ship/)）。

## 測った値・出典

- 1 本ごとの値は [`probe.tsv`](probe.tsv)（`bin/act_probe.py --tsv`）。同期 45/45
  （`check_script_sync.py --dir acting-intensity-steps-new`）。
- 台本：[`script.yaml`](script.yaml)（[`make_script.py`](make_script.py) が
  `acting-matrix/script.yaml` から作る）。
- 生成：`explainer/build_voice.py --dir acting-intensity-steps-new`・45 本・
  41.5 秒（音 144.81 秒）・M2Pro-16GB・tsukasa（`timings.tsv`）。
- 前の段：[`acting-intensity/`](../acting-intensity/)（帯が空だったとき）・
  [`acting-mod-phrase-ship/`](../acting-mod-phrase-ship/)（既定の道で同じ音が出るか）。
