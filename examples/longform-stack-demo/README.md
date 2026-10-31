# 聞き比べ — 速さを振り切ると、演技の型の差は聞こえない

`projects/longform/stack-demo/` の 45.1 秒。語り手が札を読み、真白が同じ台詞
（「明日、また来るね。」）・同じ seed を、速さ（natural / very_slow / very_fast）×
演技の型（gentle / aggressive）の 6 通りで言う。

| 時刻 | 何が鳴るか |
| --- | --- |
| 0:01.4 | 導入「同じ台詞、同じ声。速さと、演技の型だけを変えます」 |
| 0:10.6 | **natural・gentle** |
| 0:14.4 | **natural・aggressive** |
| 0:21.5 | **very_slow・gentle** |
| 0:26.4 | **very_slow・aggressive** |
| 0:34.4 | **very_fast・gentle** |
| 0:37.7 | **very_fast・aggressive** |
| 0:40.6 | 結び「速さが端まで振れていると、型の差は、ほどんど聞こえません」 |

## 聴きどころ

- **0:10.6 と 0:14.4 は 2 秒離れている**（natural）。**0:21.5 と 0:26.4（遅い）・
  0:34.4 と 0:37.7（速い）は、同じ幅で並べても差が小さい。**
- 実測（`projects/longform/acting-knob-stack/`・seed 1〜5）：aggressive − gentle の f0 は
  natural **+6.7 Hz**・very_slow **+0.7**・very_fast **−1.1**。差の差は −1.84 Hz（5/5・
  p < 0.001）。**この見本は seed 1 の 1 本ずつなので、測った平均とは数 Hz ずれる。**
- 速さそのものは 1.76〜1.79 倍で開く（0:21.5 の 4.3 秒に対し 0:34.4 は 2.4 秒）。

## 作る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/stack-demo
PYTHONPATH=. $PY projects/longform/assemble.py --dir projects/longform/stack-demo
PYTHONPATH=. $PY projects/longform/check_render.py \
  projects/longform/assets/stack-demo/renders/stack-demo.wav \
  --mix projects/longform/stack-demo/mix.yaml
PYTHONPATH=. $PY projects/longform/deliver.py \
  projects/longform/assets/stack-demo/renders/stack-demo.wav \
  examples/longform-stack-demo/stack-demo.mp3 --gain -0.35
```

配布 mp3 は −16.98 LUFS・トゥルーピーク −1.04 dBTP・LRA 5.2 LU（`check_loudness.py` 合格）。
