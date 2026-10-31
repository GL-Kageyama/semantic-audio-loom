# 文末の記号と感情は、足し算になる

同じ 1 行 `明日、また来るね` で、**文末（`。` / `！`）× 感情（neutral / joy）**の
2 × 2 を seed 5 で焼いた（20 本・beta 0.7）。ほかの欄は 4 通りで共通。

    PYTHONPATH=. $PY projects/longform/acting-punctuation-stack/run.py
    PYTHONPATH=. $PY bin/act_probe.py --tsv …/voice/*.wav > probe.tsv

## f0（seed 5 の平均・1 本ごとの f0 中央値を平均したもの）

`。` / `！` の差は、seed ごとの対の差の平均。

| | `。` | `！` | `！` − `。` |
| --- | --- | --- | --- |
| neutral | 297.2 Hz | 336.7 Hz | **+39.5 Hz**（5/5） |
| joy | 313.8 Hz | 354.1 Hz | **+40.3 Hz**（5/5） |
| joy − neutral | **+16.6 Hz**（5/5） | **+17.4 Hz**（5/5） | — |

## 2 つのこと

1. **記号の効きは、感情を替えても動かない**（+39.5 → +40.3 Hz）。**感情の効きも、
   記号を替えても動かない**（+16.6 → +17.4 Hz）。**2 つは独立で、足し算になる。**
   4 通りの和は neutral・`。` の 297.2 から **+56.9 Hz**（記号 +39.5 と感情 +16.6 の和 56.1）。
2. 強い欄どうしが足し算にならなかった組（速さ × pitch・`acting-knob-stack-speed-pitch/`）
   とは違う。**台詞の字面と Direction は、別の層として効いている。**

## 注意

- seed 5 本の平均で、符号は 5/5 だが幅は広い（記号の差 +17.6〜+62.4 Hz）。
  1 本ずつの値は `probe.tsv`。
- 感情の差 +16.6 Hz は、`acting-emotion-ladder/` の neutral → joy（**+23.9 Hz**・5/5）と
  同じ向きで、小さい。こちらは強度 0.4 の joy で測ったため。
