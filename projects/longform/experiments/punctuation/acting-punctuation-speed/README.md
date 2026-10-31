# 記号の効きは、速さを振っても消える（速さは高さを動かさない）

速さは `beta` に依らない、いちばん頼れる欄（`experiments/delivery/acting-speed/`）。記号は欄より強い。
両方を掛けたとき、効きは残るか・足し算になるか。同じ行 `明日、また来るね` の末尾
（`。` / `！`）× `speed` 3 段（very_slow / natural / very_fast）× seed 5 = 30 本。
ほかの欄は共通（neutral・moderate・pitch natural・delivery controlled・breathiness none・
`beta` 0.7）。

    PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/experiments/punctuation/acting-punctuation-speed
    PYTHONPATH=. $PY bin/act_probe.py --tsv …/voice/*.wav > probe.tsv

## 測った値（f0 は 1 本ごとの中央値を seed 5 本で平均）

| `speed` | `。` | `！` | `！` − `。` | 長さ（`。`） | 速さ（モーラ/秒） |
| --- | --- | --- | --- | --- | --- |
| very_slow | 286.3 Hz | 316.7 | **+30.4（5/5・+22.3〜+45.4）** | 4.203 s | 4.64 |
| natural | 290.3 | 332.4 | **+42.2（5/5・+28.0〜+65.8）** | 3.043 | 5.42 |
| very_fast | 295.2 | 352.3 | **+57.1（5/5・+31.8〜+86.4）** | 2.363 | 5.94 |

`speed` の側（`。` の行・natural との差）:

| `speed` | f0 の差 | 長さ |
| --- | --- | --- |
| very_slow | **−3.9 Hz（1/5）** | +1.160 秒 |
| very_fast | +4.9 Hz（4/5） | −0.680 秒 |

## 読み方

- **記号の効きは、速さを 3 段振っても消えない**（どの段も 5/5・+30.4〜+57.1 Hz）。
  **速い行ほど記号の効きが大きい**（+30.4 → +42.2 → +57.1）。ただし 1 本ずつの幅が
  広く（+22〜+86）、段の差（26.7 Hz）が幅より小さい。
- **速さは、高さをほとんど動かさない**（very_slow −3.9・very_fast +4.9 Hz）のに、
  **長さは 4.20 → 2.36 秒と 1.84 秒動く**（モーラ/秒 4.64 → 5.94）。
  記号が高さ（+42 Hz・長さ −0.16 秒）、速さが長さ（−1.84 秒・高さ +5 Hz）——
  **二つのノブは別の側を動かしている**。足し算・引き算の議論にならない。
- 同じ行・同じ seed なので、natural の行は `experiments/punctuation/acting-punctuation-pitch/` の
  natural（290.3 → 332.4）と一致する。

⚠️ 1 行・1 声・neutral だけ・seed 5 本・`beta` 0.7 だけ。`speed` は 3 段だけ
（早口・間・very_slow の 5 語のうち 3 語）。
