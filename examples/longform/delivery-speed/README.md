# 聞き比べ — 速さを振り切ると、消える型と消えない型がある

`projects/longform/experiments/demos/delivery-speed-demo/` の 53.5 秒。語り手が札を読み、真白が同じ台詞
（「明日、また来るね。」）・同じ seed（4）を、速さ（natural / very_fast）×
演技の型（gentle / aggressive / flat）の 6 通りで言う。

| 時刻 | 何が鳴るか |
| --- | --- |
| 0:01.3 | 導入「同じ台詞、同じ声。平らな言い方と、強い言い方。速さを変えたとき、どちらが残るでしょう」 |
| 0:14.5 | **natural・gentle** |
| 0:20.5 | **natural・aggressive** |
| 0:26.8 | **natural・flat** |
| 0:36.3 | **very_fast・gentle** |
| 0:40.9 | **very_fast・aggressive** |
| 0:45.7 | **very_fast・flat** |
| 0:48.6 | 結び「速くすると、強さは消えます。平らさは、残ります」 |

## 聴きどころ

- **0:20.5 と 0:14.5 の差は、0:40.9 と 0:36.3 では消える。** この 2 本は長さもほぼ同じで、
  f0 は 358.6 → 355.5 Hz（−3.1）にしかならない。**強く言っても、優しく言っても同じ声。**
- **0:26.8 と 0:45.7 の「平ら」は、速くしても残る。** f0 は natural 322.2（gentle から −25.1）、
  very_fast 339.4（gentle から −18.1）で、**差は縮むが消えない。**
- この 6 本の実測（`act_probe`）：

| speed | gentle | aggressive | flat |
| --- | --- | --- | --- |
| natural | 347.3 Hz / 3.47 s | **358.6 Hz / 3.52 s** | **322.2 Hz / 2.92 s** |
| very_fast | 357.5 Hz / 2.77 s | 355.5 Hz / 2.77 s | 339.4 Hz / 2.27 s |

- ⚠️ **この見本は seed 4 の 1 本ずつ**。seed 1〜5 の平均は
  aggressive − gentle が natural +6.7 → very_fast −1.1 Hz、flat が −18.4 → −21.4 Hz
  （`projects/longform/experiments/basics/acting-knob-stack/`・`experiments/basics/acting-knob-stack-cold/`）。
  **平均では flat は端でも広がるが、seed 4 では縮む**——1 本の見本は平均の代理でない。

## 作る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/experiments/demos/delivery-speed-demo
PYTHONPATH=. $PY projects/longform/assemble.py --dir projects/longform/experiments/demos/delivery-speed-demo
PYTHONPATH=. $PY projects/longform/check_render.py \
  projects/longform/assets/delivery-speed-demo/renders/delivery-speed-demo.wav \
  --mix projects/longform/experiments/demos/delivery-speed-demo/mix.yaml
PYTHONPATH=. $PY projects/longform/deliver.py \
  projects/longform/assets/delivery-speed-demo/renders/delivery-speed-demo.wav \
  examples/longform/delivery-speed/delivery-speed-demo.mp3 --gain -0.35
```

配布 mp3 は −16.39 LUFS・トゥルーピーク −1.06 dBTP・LRA 4.8 LU（`check_loudness.py` 合格）。
