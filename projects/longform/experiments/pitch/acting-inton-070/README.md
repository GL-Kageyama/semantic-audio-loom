# intonation の 5 語を並べても、語尾は語の名前に従わない

`intonation` は 5 語（neutral / rising / wavering / flat / falling）。
`prosody.intonation` は「subtext を語尾の傾きへ落とす」欄で、Resolve が
抽象文をここへ変換する（`docs/resolve.md`）。**5 語を同じ条件で振ると、
声の高さは seed の 11 分の 1 しか動かず、語尾の傾きは語のラベルと一致しない。**

## 同じ行・同じ感情で、intonation だけを振る

1 行「明日、また来るね。」・mashiro・neutral・moderate・volume normal・speed natural・
delivery controlled・seed 1〜5。rising / flat / falling は `experiments/pitch/acting-inton-070/script.yaml`、
neutral / wavering は `projects/longform/experiments/pitch/acting-intonation2/`（5 語 × 5 seed = 25 本）。

| intonation | f0 (Hz) | neutral との差 | 同符号 | p | 語尾の傾き (st/s・中央値) |
| --- | --- | --- | --- | --- | --- |
| rising | 293.5 | +3.3 | 3/5 | 0.26 | −0.35 |
| wavering | 291.4 | +1.1 | 2/5 | 0.21 | **3.18** |
| neutral | 290.3 | — | — | — | 2.71 |
| flat | 287.0 | −3.2 | 0/5 | 0.031 | 2.11 |
| falling | **285.8** | −4.5 | 0/5 | 0.034 | **−1.64** |

**5 語の幅は 7.7 Hz**（rising 293.5 → falling 285.8）。同じ 5 語それぞれの seed 5 本の
幅は **74〜87 Hz**（neutral 84.6・wavering 86.4・falling 86.8）。**語を替えた差は、
seed を替えた差の 11 分の 1。**

## 語尾の傾きは、ラベルと一致しない

`f0_end_st_s` は「最後の有声区間の末尾 200ms の傾き」（正が上がる）。5 seed の中央値。

| intonation | 語尾の傾き (st/s) | 名前に期待される向き |
| --- | --- | --- |
| wavering | **3.18（5 語で最大）** | 揺れる |
| neutral | 2.71 | どちらでもない |
| flat | 2.11 | 平ら |
| rising | **−0.35（4 番目）** | 上がる |
| falling | **−1.64（最小）** | 下がる |

- **名前どおりなのは falling だけ。** rising は最大にならない（4 番目）。
- neutral との差は wavering +0.47（3/5・p = 0.35）、rising −3.06（3/5・p = 0.43）で、
  **どちらも seed の振れ（−30〜+24 st/s）に隠れる**。平均で見ると seed 5 の
  rising −29.7 が効いて rising が最小になるが、**中央値では falling が最小**。
- 25 本のうち、同じ seed の中で 2 語が **0.05 Hz 以内で一致**する組が
  **50 組中 9 組**（seed 2 は 5 語とも 280.5 Hz）。**語が捨てられている seed がある。**
- 床（beta 0.0）と 0.3 でも同じ（`experiments/pitch/acting-inton-000/`・`experiments/pitch/acting-inton-030/`）。
  語の幅は 11.3 / 8.4 Hz、seed の幅は 4〜47 Hz。**floor では語のほうが seed より
  大きい**（11.3 Hz 対 4.1〜9.3 Hz）。ただし **f0 の順序は beta で入れ替わる**
  （0.0 は rising 237.8 が最小、0.3 は rising 265.7 が最大）。
- **語尾の傾きだけは、床でラベルどおりになる**（0.0 の中央値は rising +14.73 >
  flat +14.14 > falling +13.78 で 5/5）。だが**どの語も大きく上向き**で、語の差は
  0.95 半音/秒。**傾きを決めているのはプロンプトの文面で、語はその上に小さく乗る。**

## M0 の 40 Hz 差は、語の差ではなかった

`docs/resolve.md` の M0 実測は wavering で約 325 Hz、flat で約 285 Hz と、
**40 Hz の差**を報告している（「同一台詞・同一 Direction・State のみ変更」）。

同じ 2 語を、State も含めて全部固定して振った今回の実測は **291.4 対 287.0（4.4 Hz）**。
**40 Hz の差は再現しない。** M0 で動いていたのは語ではなく、
state（「返事が怖い」対「どうでもいい」）の側だったと読める——
**Resolve が状態から語を選ぶことには意味があるが、選ばれた語が声を動かす保証は無い。**

## 何が言えるか

- **`intonation` は 5 語とも実質同じ声。** 唯一の傾向は flat / falling が
  少し低い（−3〜−4 Hz・5/5）ことだけで、幅は `intensity` の 1 段より小さい。
- **語尾を「上げる／下げる」演技は、この欄では作れない。** 語尾の傾きは
  seed で −30〜+24 st/s に散り、語のラベルより seed が 1 桁大きい。
- subtext を音に乗せたいなら、`intonation` ではなく **`speed`・`pitch`・`delivery`
  の動く語**へ落とす。Resolve の変換先を変える根拠がここにある。

## 限界

- 1 行・1 人物（mashiro）・1 感情（neutral）・beta 0.7 が主。台詞が長い／疑問文だと
  語尾の傾きの測りかたが変わる可能性は残る。
- 「揺れる」を測る計器は無い（`f0_end_st_s` は末尾 200ms の直線の傾きで、
  揺れ＝分散は見ていない）。**wavering が揺れていないとは言えない。**
- f0 の中央値と末尾の傾きだけで見た。抑揚の幅（`f0_range_st`）は 5 語とも
  7.1〜7.5 半音で動かない。

## 測る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/experiments/pitch/acting-inton-070
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/experiments/pitch/acting-intonation2
PYTHONPATH=. $PY bin/act_probe.py --tsv projects/longform/assets/acting-inton-070/voice/*.wav \
  > projects/longform/experiments/pitch/acting-inton-070/inton.tsv
PYTHONPATH=. $PY bin/act_probe.py --tsv projects/longform/assets/acting-intonation2/voice/*.wav \
  > projects/longform/experiments/pitch/acting-intonation2/probe.tsv
```
