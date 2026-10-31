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
- ここで試した文言は 1 つ。**別の文言を置けば別の大きさになる**（次節で 2 つ足した）。

## 「抑える」は、抑える動作にならない

sadness は文言に反応する。では**「出さない」と書けば、声は抑えられるのか**。
同じ帯（moderate）に 3 つの文言を置いて、seed 5 本ずつ作った
（`acting-sadness-heldback/`・`acting-sadness-open/`）。

| 文言 | f0 | 文言なしとの差 | 同符号 | p |
| --- | --- | --- | --- | --- |
| （なし） | 294.4 | — | — | — |
| the feeling is present, but held back | 296.6 | +2.2 Hz | 5/5 | 0.005 |
| the feeling is steady and open | 299.9 | +5.4 Hz | 5/5 | 0.007 |
| the feeling is moderately strong | 303.9 | **+9.4 Hz** | 5/5 | 0.0015 |

- **「抑える」は下がらない。** むしろ少し上がる（+2.2 Hz・5/5）。**抑制は、量を減らす
  動作としては出ない。**
- anger でも同じ文言を試した（`acting-anger-heldback/`・5 seed）。**こちらも上がる**
  （+3.6 Hz・5/5・p = 0.0005）。**2 感情で同じ向き。**
- joy も試した（`acting-joy-heldback/`・5 seed）。**動かない**（+0.3 Hz・2/5・
  p = 0.69・差は −2.0〜+2.0 Hz）。**joy は moderate の時点で飽和している**
  （真ん中の文言でも +1.7 Hz・4/5・p = 0.072）ので、文言を足しても上がりようがない。
- **この文言はどの感情でも下げない**（sadness 5/5・anger 5/5 が上、joy は 5 本の差が
  −2.0〜+2.0 Hz で 2/5・p = 0.69）。
  上がり幅は、その文言が「どれだけ感情を主張しているか」の順
  （moderately strong > steady and open > held back > なし）。
- energy は 4 条件で ±0.5 dB（どれも n.s.）。**動くのは高さだけ。**

## 台詞を替えても、同じ形（2 行目・60 本）

1 行目だけでなく、2 行目「そんなこと、ないよ。」でも 4 段 × 3 感情 × seed 5 を作った
（`acting-intensity-line2/`）。基準線を置かず、同じ感情・同じ seed の中で段を比べる。

| 感情 | subtle | moderate | strong | overwhelming |
| --- | --- | --- | --- | --- |
| anger | 291.9 | 290.1 | 314.7 | 311.4 |
| joy | 295.1 | 295.9 | 315.9 | 301.6 |
| sadness | 290.9 | 291.5 | 308.6 | 298.0 |

| 段の間 | anger | joy | sadness |
| --- | --- | --- | --- |
| subtle → moderate | −1.8 Hz（0/5） | +0.8 Hz（2/5） | +0.6 Hz（3/5） |
| moderate → strong | **+24.6 Hz（5/5）** | **+19.9 Hz（5/5）** | **+17.1 Hz（5/5）** |
| strong → overwhelming | −3.4 Hz（0/5） | −14.2 Hz（2/5） | −10.6 Hz（0/5） |

- **真ん中が動かないこと・strong で跳ねることは、台詞を替えても同じ。**
- **上端は、2 行目では 3 感情とも strong 以下**（1 行目は anger・joy が ±1 Hz で同じ、
  sadness が −8.8 Hz）。**6 通りの平均はすべて strong 以下（−14.2〜+0.7 Hz）。**
  「最大」の語は、強さの語を超えない。
- ⚠️ **跳ね幅は seed に強く依る。** 2 行目の joy は seed 4 で +59 Hz、seed 2 で +1.5 Hz。
  5 本の符号はそろっても（5/5）、t 検定は anger p = 0.17・joy p = 0.13 で通らない。
  **「そろって上がる」と「大きさが読める」は別。**

## もうひとつの声でも、subtle と moderate は同じ段

ここまでは mashiro の声だけで測っている。演劇のもう一人（niji）は 42 本のうち
41 本が subtle か moderate に座っているので、**その 2 語が別の段かどうかは、
この作品の聞こえかたをそのまま決める**。niji・同じ行・3 感情（演劇で niji が
実際に使う calm / joy / guilt）× seed 5 本で測った（`acting-niji-intensity/`）。

| 感情 | subtle | moderate | 差 | 同符号 | p |
| --- | --- | --- | --- | --- | --- |
| calm | 313.9 | 312.8 | −1.2 Hz | 1/5 | 0.18 |
| joy | 329.1 | 329.4 | +0.3 Hz | 2/5 | 0.72 |
| guilt | 304.4 | 306.5 | +2.0 Hz | 5/5 | 0.001 |

**3 感情とも ±2 Hz の中。** guilt だけ符号がそろう（5/5・p = 0.001）が、大きさは
2 Hz で、mashiro での 2 段の差（±3 Hz）と同じ帯。seed の振れの前では、段として
聴こえる差ではない。

**声を替えても、感情を替えても、subtle と moderate は 1 段のまま。**

## 作品は、どの段に座っているか

2 段しかないなら、台本がどこに座っているかを数える意味がある
（`projects/longform/acting/knob_audit.py`）。

| 作品 | 人物 | 本数 | 同じ段（subtle+moderate） | strong 以上 |
| --- | --- | --- | --- | --- |
| explainer | narrator | 44 | **44（100%）** | 0 |
| explainer | mashiro | 4 | 2（50%） | 2 |
| drama | mashiro | 47 | 38（81%） | 9 |
| drama | niji | 42 | **41（98%）** | 1 |

- **解説の語り手は、44 本すべてが同じ段。** 強度を書いても、聴き手には 1 段しか届かない。
- **演劇は 89 本のうち 79 本（89%）が同じ段。** 聴こえる強弱は「平ら」と「上げた」
  の 2 値で、その境目は 10 本。
- 台本の上では subtle 51 回・moderate 28 回と書き分けている。**書き分けは、
  この計器では 1 つに畳まれる。**
### 畳まれた段は、作品の中で聞こえるか

2 段に畳まれることが、実際の作品で「同じ声」を作っているかを、全キュー総当たりで
確かめた（`near_duplicates.py`・声質の距離・しきい値 8.0 は結果を見る前の既定）。

| 作品 | 本数 | 組 | 中央値 | 8.0 未満 |
| --- | --- | --- | --- | --- |
| drama | 89 | 3,916 | 40.27 | 1 組（0.00） |
| explainer | 48 | 1,128 | 23.08 | 12 組（3.8〜7.2） |

- **演劇の 0.00 は、書き手が意図した同文反復**（`s01` と `s68` は同じ台詞
  「……もしもし。」に同じ演技と seed）。**それ以外に 8.0 未満の組は無い。**
  6.90 の組（`s25`↔`y07`）は、台詞が「……それだけ。」と「それだけ。」で実質同じ。
- **解説の 12 組のうち 11 組は、語り手どうし**（台詞が違い、設定もほぼ同じ）。
  中央値 23.08・下位 5% 9.97 に対して、この 11 組は 3.8〜7.2 ——**台詞だけで動く
  計器の下限**がここに来ている。
- **残る 1 組が、この作品の弱点を突いている**：`m02`↔`m04` は**同じ台詞・同じ seed**で、
  strong/loud/fast/cheerful と subtle/normal/natural/gentle を振った組。距離 4.52 で、
  **台詞の違う語り手の組（3.8〜7.2）と同じ帯**。設定を 4 つ変えても、この 2 本は
  「別の演技」の距離まで離れていない。
- ⚠️ **距離は台詞に強く依る**（同じ人物・同じ設定でも、台詞が違えば 3.8〜40 動く）。
  **この計器で言えるのは「同じ台詞どうしの比較」まで。**
- **つまり、2 段に畳まれることは 89 本の作品を平坦にはしない**（台詞の違いのほうが
  大きい）。**平坦になるのは、同じ台詞を 4 つの設定で並べたとき**——解説の
  `m02`/`m04` がその実例。一覧は `REPORT.md`「全キュー総当たりで…」にある。

- 声量は事情が違う（`acting-volume/`）。**声そのものは声量の語に反応しない**
  （whisper と loud で energy 0.08 dB）が、`assemble.py` の `VOLUME_GAIN` が
  −10 / −5 / 0 / +3 / +6 dB を掛けるので、**ミックスでは 5 段ある**。
  強度にはその受け皿が無い（掛ける先が高さで、ミックスでは作れない）。

## 限界

- 1 行・1 人物（mashiro）・3 感情。感情を増やせば、上端の向きは変わりうる。
  **台詞は 2 行試した**（1 行目と 2 行目で形は同じ・跳ね幅は違う）。
- 2 行目は基準線（neutral）を置いていないので、**感情の効きは 2 行目では測っていない**。
- beta 0.7 の 5 語のうち、none は測っていない（moderate と同じ散文なので同じ音になる）。
- 「真ん中の文言」は 3 つだけ試した。**別の文言なら別の大きさになる**（ここで言えるのは
  「語を足せば上がる。強さの語ほど大きく上がる」まで）。
- 抑える演技は sadness・anger・joy の 3 感情で試した。**残る 6 感情は試していない。**
- 強度の効果は、`emotion-seed/` の seed の振れ（同一人物・同じ行で 84.6 Hz）より小さい。
- 長さ・抑揚の段差は、**この行が短い**（3 秒前後）ので、長い台詞で同じ割合になるかは
  測っていない。

## 測る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/acting/intensity_steps.py           # 1 行目（4 段 + 上端）
PYTHONPATH=. $PY projects/longform/acting/intensity_steps.py --line2   # 2 行目（4 段）
```

上の表と検定は、`acting-matrix/matrix.tsv`（subtle / moderate / strong × 5 seed）と
`acting-overwhelming-070/probe.tsv`（overwhelming × 5 seed）を読んで出す。

文言を差し替えた版は、原本を触らずに作れる（表をプロセスの中だけで差し替える）。

```bash
PYTHONPATH=. $PY projects/longform/acting/mod_phrase_build.py \
  --dir projects/longform/acting-sadness-heldback \
  --phrase "the feeling is present, but held back" --band 0.70
```
