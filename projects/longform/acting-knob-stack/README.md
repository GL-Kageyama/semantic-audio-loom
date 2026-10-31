# 速さを振り切ると、演技の型（delivery）の効きが消える

`speed` は 5 段、`delivery` は 3 段——**だが 2 つを同時に振ったことは無かった。**
同じ行・joy・moderate・breathiness none・seed 1〜5 で、`speed`（very_slow / very_fast）×
`delivery`（gentle / aggressive）の 4 通り 20 本を作った。

| speed | delivery | 長さ (s) | f0 (Hz) | 間の割合 | 抑揚 (半音) |
| --- | --- | --- | --- | --- | --- |
| very_slow | gentle | 4.41 | 309.9 | 0.23 | 8.18 |
| very_slow | aggressive | 4.34 | 310.6 | 0.23 | 8.22 |
| very_fast | gentle | 2.46 | 327.1 | 0.23 | 8.02 |
| very_fast | aggressive | 2.46 | 326.0 | 0.23 | 8.16 |

## 速さの効きは、演技の型の側でも変わらない

| 効き | gentle の側 | aggressive の側 |
| --- | --- | --- |
| 長さ（very_fast − very_slow） | **−1.95 秒**（0/5・p = 3e−06） | **−1.88 秒**（0/5・p = 4e−06） |
| f0（very_fast − very_slow） | **+17.2 Hz**（5/5・p = 0.014） | **+15.3 Hz**（5/5・p = 0.019） |
| 間の割合 | −0.00（3/5） | +0.00（3/5） |

- **1.79 倍と 1.76 倍。** 速さの段は、delivery が何であっても同じだけ開く。
- **速さは f0 も動かす。** 5 段の平均は 306.0 → 312.6 → 314.2 → 319.5 → 320.8 Hz で、
  **遅い端と速い端の差は +14.8 Hz**（`acting-speed/`・seed ごとでは 4/5）。
  **段の途中は単調でなく、両端だけが離れる。**
- 間の割合は 0.23 のまま動かない。**伸び縮みしているのは発話そのもの。**

## 演技の型の効きは、速さの端で消える

| speed | aggressive − gentle（f0） | 同符号 | p |
| --- | --- | --- | --- |
| natural（`acting-delivery/`） | **+6.7 Hz** | 5/5 | 0.0085 |
| very_slow | +0.7 Hz | 2/5 | 0.18 |
| very_fast | **−1.1 Hz** | 0/5 | 0.075 |

- **差の差（very_fast の差 − very_slow の差）は −1.84 Hz・5/5・p < 0.001。**
  つまり**交互作用がある。**
- 速さの端では、gentle と aggressive の f0 が **0.1 Hz まで一致する seed がある**
  （seed 3・seed 5）。WAV の長さも同じで、**語は届いているのに音が同じ**。
- 読みかた：`delivery` の効き幅（±7 Hz）は `speed` の効き幅（±15 Hz）より小さく、
  **速さが振り切れていると、型の差はその中に埋まる。**

## 何が言えるか

- **上へ動かす型は、速さの端で消える。** 強い欄（speed）を端まで振ると、`aggressive` の
  差は 0 になる。
- ⚠️ **これは「どの型でも消える」ではない。** 下へ動く `cold` / `flat` は速さの端でも
  残る（`acting-knob-stack-cold/`）。`pitch` を振ったときは半分残る
  （`acting-knob-stack-pitch/`）。**消える型と消えない型がある。**
- 速さの段は堅い（1.79 倍・両方の delivery で 0/5）。
- **f0 も動く。**「速さは長さだけ」ではない——遅い端と速い端で 15〜17 Hz 開く。
  ただし y 軸を「演技の強さ」と読むと、**速くすると高くなる**（強い、とは別）。

## 限界

- 1 行・1 人物（mashiro）・1 感情（joy）。delivery は gentle / aggressive の 2 語だけ。
  下へ動く cold / flat は `acting-knob-stack-cold/`、pitch との組み合わせは
  `acting-knob-stack-pitch/` で測った。
- **natural の行だけ別の実験（`acting-delivery/`）から持ってきた。** 同じ行・同じ感情・
  同じ seed だが、焼いた日が違う。
- 「消えた」を測ったのは f0 と長さだけ。息・声質は見ていない。

## 測る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/acting-knob-stack
PYTHONPATH=. $PY bin/act_probe.py --tsv projects/longform/assets/acting-knob-stack/voice/*.wav \
  > projects/longform/acting-knob-stack/probe.tsv
PYTHONPATH=. $PY projects/longform/check_script_sync.py --dir projects/longform/acting-knob-stack
```
