# 聞き比べ — 音の高さの 6 語を、低い順に並べる

`projects/longform/experiments/demos/pitch-demo/` の 47.2 秒。語り手が「とても低く」から「高く」まで札を読み、
真白が同じ台詞（「明日、また来るね。」）・同じ seed（4）を 6 通りで言う。

| 時刻 | 札 | `pitch` | f0（seed 4 のこの 1 本） |
| --- | --- | --- | --- |
| 0:01.4 | 導入「同じ台詞を、六つの音の高さで言います。低いほうから、順に」 | — | — |
| 0:10.2 | とても低く | `very_low` | **327.8 Hz** |
| 0:15.6 | 低く | `low` | 329.7 Hz |
| 0:21.6 | 少し低く | `slightly_low` | 335.5 Hz |
| 0:27.2 | ふつう | `natural` | **343.4 Hz** |
| 0:33.0 | 少し高く | `slightly_high` | 337.5 Hz |
| 0:38.1 | 高く | `high` | **343.4 Hz** |
| 0:41.8 | 結び「六つの高さは、ほとんど同じに聞こえます。高くする語は、ありません」 | — | — |

## 聴きどころ

- **`high` と `natural` は同じ高さ**（343.4 Hz・同じ 1 本では同値）。**「高く」は高くしない。**
- **`slightly_high` は `natural` より低い**（337.5 Hz）。**名前と向きが逆。**
- **下がるのは当てにできる**：`very_low` 327.8・`low` 329.7 は natural より 14〜16 Hz 低い。
  `very_low` と `low` の差は 1.9 Hz で、**2 語で 1 段**。
- 全体の幅は **15.6 Hz**（327.8〜343.4）。同じ台詞の `speed` の両端（very_slow ↔ very_fast）が
  +15〜17 Hz 動くのと、**同じくらいの幅しかない**。

## 6 本の実測（`act_probe`）

| pitch | f0 (Hz) | 長さ (s) |
| --- | --- | --- |
| very_low | 327.8 | 3.50 |
| low | 329.7 | 3.50 |
| slightly_low | 335.5 | 3.37 |
| natural | 343.4 | 3.32 |
| slightly_high | 337.5 | 3.30 |
| high | 343.4 | 3.35 |

- ⚠️ **この見本は seed 4 の 1 本ずつ**。seed 10 本の平均は very_low 299.0 / low 302.0 /
  slightly_low 309.7 / natural 315.5 / slightly_high 312.9 / high 315.4 Hz
  （`projects/longform/experiments/pitch/acting-pitch-ladder/`）。**1 本の見本は平均の代理でない**
  （ここでは全体が 25〜29 Hz 高く出ている——seed 4 は 10 本の中で高い側）。
  ✅ この 6 本は、`experiments/pitch/acting-pitch-ladder/` の seed 4 の 6 本と**同じ値**（別プロセス・別の置き場）。

## 作る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/experiments/demos/pitch-demo
PYTHONPATH=. $PY projects/longform/assemble.py --dir projects/longform/experiments/demos/pitch-demo
PYTHONPATH=. $PY projects/longform/check_render.py \
  projects/longform/assets/pitch-demo/renders/pitch-demo.wav --mix projects/longform/experiments/demos/pitch-demo/mix.yaml
PYTHONPATH=. $PY projects/longform/deliver.py \
  projects/longform/assets/pitch-demo/renders/pitch-demo.wav \
  examples/longform/pitch/pitch-demo.mp3 --gain -0.35
```

配布 mp3 は −16.43 LUFS・トゥルーピーク −1.01 dBTP・LRA 5.50 LU（`check_loudness.py` 合格）。
