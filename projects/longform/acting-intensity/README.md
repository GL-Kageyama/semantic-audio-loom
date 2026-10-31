# 強度の段は、いくつあるか

Direction の強度は 5 語（none / subtle / moderate / strong / overwhelming）。
語は 5 つあるが、**声を動かす段は 2 つ**。真ん中が真ん中でなく、上端は感情によって
逆へ振れる。

## 語は 5 つ、散文は 3 つ

`semantic_audio_loom/providers/tsukasa.py` の `_INTENSITY_PHRASES` が、強度を
プロンプトの一言に変える。解決後の値（`engine/resolve.py` の `INTENSITY_MAP`）と対応させる。

| 語 | 値 | プロンプトに足される一言 |
| --- | --- | --- |
| none | 0.0 | （なし） |
| subtle | 0.25 | the feeling is faint, barely showing |
| moderate | 0.5 | **（なし）** |
| strong | 0.75 | the feeling is strong, close to the surface |
| overwhelming | 1.0 | the feeling is overwhelming, at its limit |

**none と moderate は、散文が同じ（どちらも何も足さない）。** 5 語はプロンプトの上で
4 段、実質は「faint」「なし」「strong」「overwhelming」の 3 種＋なし。

## 既定の混ぜ方（beta 0.7）では 2 段

同じ 1 行・同じ人物・seed 1〜5。基準線は neutral / moderate（f0 平均 290.3 Hz）。

| 感情 | subtle | moderate | strong | overwhelming |
| --- | --- | --- | --- | --- |
| anger | 312.6 | 310.0 | 320.0 | 320.7 |
| joy | 313.8 | 314.2 | 323.0 | 323.0 |
| sadness | 295.3 | 294.4 | 312.8 | **304.0** |

seed 5 本そろえた差の検定（1 標本 t・差が 0 か）:

| 段の間 | anger | joy | sadness |
| --- | --- | --- | --- |
| subtle → moderate | −2.7 Hz（0/5） | +0.4 Hz（1/5・n.s.） | −0.8 Hz（1/5・n.s.） |
| moderate → strong | **+10.0 Hz（5/5）** | **+8.8 Hz（5/5）** | **+18.3 Hz（5/5）** |
| strong → overwhelming | +0.7 Hz（3/5・n.s.） | +0.0 Hz（3/5・n.s.） | **−8.8 Hz（0/5）** |

- **跳ねるのは moderate → strong の 1 か所だけ。** subtle と moderate は ±3 Hz で、
  基準線そのものの seed 5 本の幅（84.6 Hz・241.4〜326.0）に埋もれる。
- **上端は伸びない。** anger・joy では strong と overwhelming が同じ高さ（差 1 Hz 未満）。
  **sadness だけ下がる**（5 seed すべて）。
- **強度の主な出口は高さ。** ただし高さだけではない——moderate → strong で長さが
  anger +0.08 秒・joy +0.14 秒（どちらも 5/5・p ≤ 0.016）、sadness で抑揚が
  +0.44 半音（5/5・p = 0.009）動く。**energy は 5 本とも下がり気味だが p ≥ 0.14
  （joy −0.52 dB・sadness −0.62 dB）、速さは動かない**（p ≥ 0.42）。

## sadness の上端は、混ぜ方を下げると大きく戻る

既定 0.7 で −8.8 Hz だった差が、beta 0.3（感情の重みを上げた側）ではもっと大きい
（`acting-intensity-sadness/`・3 本ずつ）。

| seed | strong | overwhelming | 差 |
| --- | --- | --- | --- |
| 1 | 345.3 | 318.5 | −26.8 |
| 2 | 324.1 | 295.5 | −28.6 |
| 3 | 333.6 | 305.9 | −27.7 |

**3 seed とも −27 Hz 前後。** seed の偶然ではなく、「at its limit」の一言が sadness では
高さを下げる側に働く。energy は +0.9 dB（strong −16.3 → overwhelming −15.4）。

## 真ん中の段に、文言を置いたら

真ん中が動かないのは、**真ん中に文言が無いから**ではないか。0.4〜0.7 の帯に
"the feeling is moderately strong" を差し込んで、moderate だけを作り直した
（`acting-mod-phrase/`・15 本。ビルドは `acting/mod_phrase_build.py`。原本は触らず、
プロセスの中で表を差し替える）。比べる相手は同じ設定・文言なしの `em-<感情>`。

| 感情 | 差（文言あり − なし） | 同符号 | p |
| --- | --- | --- | --- |
| anger | +1.3 Hz | 4/5 | 0.028 |
| joy | +1.7 Hz | 4/5 | 0.072 |
| sadness | **+9.4 Hz** | 5/5 | 0.0015 |

- **sadness だけ動く。** strong の +18.3 Hz の半分ほど。**sadness は文言に敏感で、
  anger・joy は moderate の時点でほぼ飽和している。**
- anger・joy の +1〜2 Hz は、seed の振れの前では「動いた」と言える大きさではない
  （anger の p は 0.028 だが、5 本の差は +2.1〜+0.0 Hz）。

## 限界

- 1 行・1 人物（mashiro）・3 感情。感情を増やせば、上端の向きは変わりうる。
- beta 0.7 の 5 語のうち、none は測っていない（moderate と同じ散文なので同じ音になる）。
- 「真ん中の文言」は 1 つだけ試した。**別の文言なら別の大きさになる**（ここで言えるのは
  「文言を置けば sadness は動く」まで）。
- 強度の効果は、`emotion-seed/` の seed の振れ（同一人物・同じ行で 84.6 Hz）より小さい。
- 長さ・抑揚の段差は、**この行が短い**（3 秒前後）ので、長い台詞で同じ割合になるかは
  測っていない。

## 測る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/acting/intensity_steps.py
```

上の表と検定は、`acting-matrix/matrix.tsv`（subtle / moderate / strong × 5 seed）と
`acting-overwhelming-070/probe.tsv`（overwhelming × 5 seed）を読んで出す。
