# 長い台詞では、強さは「高さ」ではなく「抑揚の幅」に出る

ここまでの強度の測定は、3 秒の一言（「明日、また来るね。」）で行っている。
**長い台詞で同じ形になるか**を、芝居の実際の行（`drama` の `s47`・24 文字・句点 2 つ）
で測った。4 段 × 3 感情 × seed 5・60 本（`script.yaml`）。

台詞：「最初に会ったとき。画面の向こうで、虹が揺れてた。」（`drama` の `s47` と同じ）

## f0 の中央値（Hz）

| 感情 | subtle | moderate | strong | overwhelming |
| --- | --- | --- | --- | --- |
| anger | 278.1 | 277.9 | 281.8 | 282.4 |
| joy | 281.3 | 282.9 | 283.6 | 284.8 |
| sadness | 264.4 | 265.0 | 278.2 | **273.0** |

| 段の間 | anger | joy | sadness |
| --- | --- | --- | --- |
| subtle → moderate | −0.2 Hz（2/5） | +1.6 Hz（4/5・p = 0.040） | +0.6 Hz（2/5） |
| moderate → strong | +4.0 Hz（4/5・p = 0.076） | **+0.7 Hz（2/5・n.s.）** | **+13.2 Hz（5/5・p = 0.0014）** |
| strong → overwhelming | +0.6 Hz（3/5） | +1.2 Hz（3/5） | **−5.2 Hz（0/5・p = 0.032）** |

## 抑揚の幅（半音）

| 感情 | subtle | moderate | strong | overwhelming | moderate → strong |
| --- | --- | --- | --- | --- | --- |
| anger | 7.96 | 8.08 | 8.68 | 8.60 | **+0.60（5/5・p = 0.010）** |
| joy | 7.58 | 7.52 | 8.30 | 8.26 | **+0.78（5/5・p = 0.0041）** |
| sadness | 7.84 | 7.74 | 8.58 | 8.08 | **+0.84（5/5・p = 0.0012）** |

- **3 感情とも、moderate → strong で抑揚の幅が広がる。5 seed すべて同じ向き・p ≤ 0.01。**
- **高さ（中央値）は、3 感情のうち sadness だけが大きく動く。** joy と anger は 1〜4 Hz で、
  この行では「上がった」と言えない。
- 上端（strong → overwhelming）は、**sadness で高さ −5.2 Hz・抑揚 −0.50 半音（どちらも 0/5）**。
  anger も抑揚 −0.08。**「最大」は、強さを超えない。**

## 何が言えるか

- **2 段の形（subtle ≈ moderate、moderate → strong で跳ねる、上端は伸びない）は、
  長い台詞でも同じ。**
- ただし**跳ねる先が違う**。3 秒の一言では中央値が上がった（+8.8〜+18.3 Hz）が、
  長い行では**抑揚の幅が広がる**（+0.6〜+0.8 半音）のが確かな出口で、中央値は
  sadness でしか動かない。
- **強さは「高い声」ではなく「振れ幅の大きい声」。** 短い行では高さにしか表れようが
  なかった、と読むのが正しい。
- 長さ・energy・速さ・無音の割合は動かない（長さ ±0.1 秒・energy p ≥ 0.15・
  速さ p ≥ 0.36）。**3 秒の一言で見えた「moderate → strong で長さが +0.08〜0.14 秒」
  は、この行では再現しない。**

## 限界

- **1 行・3 感情・seed 5。** 台詞は 1 つだけ（`drama` の 1 行）。
- 抑揚の幅は、長い発話ほど自然に広がる量（この行の中での比較なので、段の差は読める）。
- 60 本すべて mashiro・beta 0.7・alpha 0.35。

## 測る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/acting-longline
PYTHONPATH=. $PY bin/act_probe.py --tsv projects/longform/assets/acting-longline/voice/*.wav \
  > projects/longform/acting-longline/probe.tsv
```
