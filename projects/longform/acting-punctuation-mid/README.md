# 真ん中の長さ（14 文字）では、短い行と同じ幅で効く

`acting-punctuation/`（9 文字）と `acting-punctuation-long/`（24 文字）のあいだを埋める。
同じ長い行から頭の 1 節を落とした 14 文字の行「画面の向こうで、虹が揺れてた」で、
末尾だけを `。` / `！` に替える（2 通り × seed 5 = 10 本）。Spec は共通
（`acting-subtext/llm-specs.json` の none＝neutral・0.5・controlled）。

    PYTHONPATH=. $PY projects/longform/acting-punctuation-mid/run.py
    PYTHONPATH=. $PY bin/act_probe.py --tsv …/voice/*.wav > probe.tsv

## 測った値

| 文末 | f0 中央値 | 長さ |
| --- | --- | --- |
| `。` | 271.0 Hz | 3.673 s |
| `！` | 322.2 Hz | 3.273 s |

`。` との差（seed ごとの対・5 本）:

| 文末 | f0 の差 | 長さの差 |
| --- | --- | --- |
| `！` | **+38.9 Hz（5/5・+34.7〜+58.7）** | **−0.250 s（0/5）** |

## 読み方

- **14 文字の行では、9 文字の行とほぼ同じ幅**（+39.3 と +38.9 Hz）。
  長さだけでは説明できない——24 文字の行で縮んだ（+13.2 Hz）のは別の理由。
  同じ 24 文字のまま途中の句点を読点に替えた対照
  （[`acting-punctuation-long/run_comma.py`](../acting-punctuation-long/run_comma.py)）は
  **+22.0 Hz（5/5）**。さらに 9 文字のまま途中を句点にした行
  （`acting-punctuation-period/`）は **+15.2 Hz（5/5）**——**途中で文が切れることが
  先で、長さは後**（5 点の表はそちらの README に置いた）。
- 長さは 5 本とも縮む（−0.250 s）。短い行・長い行と同じ向き。
