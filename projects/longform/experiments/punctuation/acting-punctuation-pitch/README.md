# 文末の記号の効きは、`pitch` を振っても残る

記号は欄より強い（`experiments/punctuation/acting-punctuation/`）。欄のうちでいちばん強い `pitch` と
掛け合わせたら、記号の効きは残るか・足し算になるか。
同じ行 `明日、また来るね` の末尾（`。` / `！`）× `pitch` 3 語（very_low /
natural / high）× seed 5 = 30 本（neutral）。`pitch` の効きが感情で変わるのを
見るため、joy × 3 語 × seed 5 = 15 本も焼いた。ほかの欄は共通
（moderate・speed natural・delivery controlled・breathiness none・beta 0.7）。

    PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/experiments/punctuation/acting-punctuation-pitch 2>&1 | tail
    PYTHONPATH=. $PY bin/act_probe.py --tsv …/voice/*.wav > probe.tsv

## 測った値（neutral・f0 は 1 本ごとの中央値を 5 本で平均）

| pitch | `。` | `！` | `！` − `。` |
| --- | --- | --- | --- |
| very_low | 276.7 Hz | 315.6 Hz | **+38.8 Hz（5/5・+22.3〜+59.7）** |
| natural | 290.3 | 332.4 | **+42.2（5/5・+28.0〜+65.8）** |
| high | 299.3 | 346.7 | **+47.4（5/5・+31.7〜+65.3）** |

`pitch` の側（`。` の行・neutral）:

| pitch | natural との差 | 符号 |
| --- | --- | --- |
| very_low | **−13.5 Hz** | 1/5 |
| high | **+9.0 Hz** | 5/5 |

## 読み方

- **記号の効きは、`pitch` を 3 段振っても消えない**（15/15 で正・+38.8〜+47.4 Hz）。
  段による差は 8.6 Hz で、1 本ずつの幅（+22〜+66 Hz）より小さい。
- **ほぼ足し算。** very_low・`。` の 276.7 から high・`！` の 346.7 まで **+70.0 Hz**。
  部品の和は 22.6（very_low → high）＋ 42.2（記号・natural で測った値）＝ 64.8 Hz。
  記号の側が high で少し伸びる（+42.2 → +47.4）。
- **`pitch` の high は、感情で効きが変わる。** neutral では high が natural より
  **+9.0 Hz（5/5）** 高いのに、**joy では +0.2 Hz（1/5）** で動かない
  （joy very_low は −12.0 Hz・0/5）。この joy の値は `experiments/pitch/acting-pitch-ladder/` の
  10 本（high −0.1 Hz）と同じ向き。**欄の効きは、感情が埋めているぶんだけ減る**
  （機序までは測っていない）。
- **記号の効き（+39〜+47 Hz）は、`pitch` の効き（−13〜+9 Hz）の 3〜5 倍。**
  neutral の high は、記号 1 つで戻ってしまう大きさ。
- 長さは `！` で縮む（natural で 3.043 → 2.883 秒・−0.16 秒）。他の行と同じ向き。

⚠️ 1 行・1 声・seed 5 本。**neutral と joy の 2 感情だけ**で、ほかの感情は測っていない。
