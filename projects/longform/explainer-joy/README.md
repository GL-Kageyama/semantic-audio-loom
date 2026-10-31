# explainer-joy — seed と演技の方向、どちらが声を動かすか

解説の「三通り」のうち、**2 つめ（励まし）と 3 つめ（照れ隠し）がほぼ同じ音**に
なっていた。その差が「方向が届いていない」のか「seed の揺れの内側」なのかを見る実験。

台詞は同じ 1 行「明日、また来るね。」。真白・seed 1・同じ解説の方向。

## 何を並べたか

| 本 | 設定 | seed |
| --- | --- | --- |
| 本番 m02 | joy / strong / loud / fast / slightly_high / cheerful | 1 |
| 本番 m04 | joy / subtle / normal / natural / slightly_high / gentle / 息すこし | 1 |
| m02 の設定 s2・s3 | m02 と同じ | 2・3 |
| m04 の設定 s2・s3 | m04 と同じ | 2・3 |
| alt 3 本 | 方向を強く振る（quiet/slow/hesitant・very_slow/cheerful・neutral/gentle） | 1 |

## 結果 — seed のほうが大きく動かす

| | f0 中央値 | 抑揚 | 包絡（m02 から） | MFCC（m02 から） |
| --- | --- | --- | --- | --- |
| 本番 m02（s1） | 355.5 Hz | 9.6 | — | — |
| 本番 m04（s1） | 355.5 Hz | 9.4 | **0.11 dB** | **5.4** |
| m02 の設定 s2 | 305.9 Hz | 6.7 | 1.06 dB | 23.1 |
| m02 の設定 s3 | 315.8 Hz | 8.6 | 0.85 dB | 15.2 |
| m04 の設定 s2 | 304.1 Hz | 6.6 | 0.95 dB | 21.6 |
| m04 の設定 s3 | 318.5 Hz | 8.6 | 1.02 dB | 19.1 |
| alt quiet/slow/hesitant | 353.4 Hz | 9.0 | 0.58 dB | 11.6 |
| alt very_slow/cheerful | 345.3 Hz | 8.6 | 0.46 dB | 17.4 |
| alt neutral/gentle | 335.5 Hz | 7.7 | 0.49 dB | 19.9 |

- **seed を替えると f0 が 50 Hz 動く**（355.5 → 304〜318）。**方向を振っても動かない**
  （345〜357）。しかも動き先は seed で決まる——m02 の設定でも m04 の設定でも、
  s2 は 305 前後、s3 は 316 前後に着地する（差 1.8〜2.7 Hz）。
- **声質も同じ向き。** 片方だけ動かして比べると——**同じ seed で方向を変えると
  MFCC 5.4・6.7・7.8**（s1・s2・s3）、**同じ方向で seed を替えると 15.2〜23.1**。
  **方向の差は、seed の揺れの内側に入る。**（包絡でも同じ——方向 0.11〜0.56 dB、
  seed 0.85〜1.06 dB。）
- 2 つめと 3 つめが似て聞こえるのは、方向が届いていないからではなく、
  **同じ seed 1 の中で方向が動かせる幅が小さい**から。

## 限界

- 1 行・1 人（真白）・3 seed。**他の行や他の人物で同じとは限らない。**
- 本番は全キュー seed 1。だから作品の中の方向の比較（演技 4 通りで 29.5 Hz）は
  seed を固定した比較として読める。**seed をまたいだ一般化はできない。**
- f0 は act_probe と librosa pyin の 2 本で確かめた（m02 338.7 / s2 297.4 / s3 314.2 Hz。
  絶対値は違うが順序と幅は同じ）。

## 作る・測る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/explainer-joy
PYTHONPATH=. $PY projects/longform/explainer-joy/measure_joy.py
```

`script.yaml` が並べる本、`measure_joy.py` が測って表を出す。
