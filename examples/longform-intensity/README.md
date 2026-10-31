# 聞き比べ — 強度は、どこから声に出るか

同じ一言（「明日、また来るね。」）・同じ seed（2）で、**強度（intensity）だけ**を
変えて並べた 63 秒の見本。語り手が札を読み、真白が毎回同じ台詞を言う。

並びは「うすい → ふつう → つよい → さいだい」の 4 段（怒り）と、
「ふつう → つよい → さいだい」の 3 段（悲しみ）。

## 並び

| 秒 | 中身 | f0 |
| --- | --- | --- |
| 0:01.4 | 導入（語り手） | — |
| 0:10.8 | 怒り・ごくうすく（subtle） | 298.9 Hz |
| 0:16.6 | 怒り・ふつう（moderate） | 297.2 Hz |
| 0:22.4 | 怒り・つよく（strong） | **307.7 Hz** |
| 0:28.5 | 怒り・さいだい（overwhelming） | 305.9 Hz |
| 0:35.8 | 悲しみ・ふつう（moderate） | 283.8 Hz |
| 0:42.0 | 悲しみ・つよく（strong） | **300.6 Hz** |
| 0:48.3 | 悲しみ・さいだい（overwhelming） | **292.1 Hz** |
| 0:52.4 | 結び（語り手） | — |

## 聴きどころ

- **0:10.8 と 0:16.6 は、同じに聞こえるはず**（差 1.7 Hz）。5 seed の平均でも
  ±3 Hz で、seed の振れ（84.6 Hz）の中。
- **0:16.6 → 0:22.4 で跳ねる**（+10.5 Hz）。この 1 段だけが「強度を上げた」音。
- **0:28.5 は 0:22.4 より高いと思えない**（−1.8 Hz）。
- **0:48.3 は 0:42.0 より低い**（−8.5 Hz）。**最大の語が、強さの語より抑えられた声**になる。

## 5 seed の平均（この見本は seed 2 の 1 本ずつ）

| 感情 | subtle | moderate | strong | overwhelming |
| --- | --- | --- | --- | --- |
| anger | 312.6 | 310.0 | 320.0 | 320.7 |
| sadness | 295.3 | 294.4 | 312.8 | 304.0 |

seed 2 でも並びは同じ（怒り +10.5 / −1.8、悲しみ +16.8 / −8.5）。
検定と解釈は [projects/longform/acting-intensity/](../../projects/longform/acting-intensity/)。

## 作る

```zsh
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/intensity-demo
PYTHONPATH=. $PY projects/longform/assemble.py --dir projects/longform/intensity-demo
PYTHONPATH=. $PY projects/longform/deliver.py \
  projects/longform/assets/intensity-demo/renders/intensity-demo.wav \
  examples/longform-intensity/intensity-demo.mp3 --gain -0.56
```

## 限界

- **1 行・1 seed。** 5 seed で同じ並びになることは測ってあるが、この見本は seed 2 の
  1 本ずつで、声の高さそのもの（283〜308 Hz）は seed 2 の値。
- 強度の差は 8〜17 Hz で、**seed を替えたときの振れ（この行で 84.6 Hz）より小さい**。
  耳で「別の演技」に聞こえるかは、ここでは測れない。
