# 聞き比べ — 同じ指示で、seed だけを替える

`projects/longform/seed-demo/` の 42.1 秒。語り手が「一回目」…と読み、真白が同じ台詞
（「明日、また来るね。」）・同じ演技（joy・moderate・natural・controlled・none）を
**seed 1〜5 で**言う。**指示は 5 本とも同じ。**

| 時刻 | 何 | seed | f0（この 1 本） | 長さ |
| --- | --- | --- | --- | --- |
| 0:01.4 | 導入「同じ言葉を、同じ演技で、五回いいます。違うのは、seed だけです」 | — | — | — |
| 0:08.5 | 一回目 | 1 | **351.4 Hz** | 2.85 s |
| 0:13.9 | 二回目 | 2 | 302.4 Hz | 3.02 s |
| 0:19.6 | 三回目 | 3 | 314.9 Hz | 2.75 s |
| 0:25.2 | 四回目 | 4 | 343.4 Hz | 3.32 s |
| 0:31.2 | 五回目 | 5 | **258.7 Hz** | 3.37 s |
| 0:37.3 | 結び「指示は五つとも同じです。声は、これだけ違います」 | — | — | — |

## 聴きどころ

- **同じ指示で、f0 が 92.7 Hz 動く**（258.7〜351.4）。長さも 0.62 秒動く（2.75〜3.37）。
- Direction の欄を 1 つ振った差は、`pitch` の 6 語で **15.6 Hz**・感情 11 語で
  **25.5 Hz**・`delivery` の 4 語で **45 Hz**（beta 0.3 のとき。0.7 では揺れの中）。
  **seed の 92.7 Hz はそのどれより大きい。seed を固定しないと欄の効きは読めない。**
- この 5 本は `acting-emotion-ladder/` の joy とは別の置き場・別のビルドだが、
  **同じ seed なら近い値**になる（seed 4 は 343.4 Hz で、`pitch-demo/` の natural
  seed 4 と同じ）。

## 作る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/seed-demo
PYTHONPATH=. $PY projects/longform/assemble.py --dir projects/longform/seed-demo
PYTHONPATH=. $PY projects/longform/check_render.py \
  projects/longform/assets/seed-demo/renders/seed-demo.wav --mix projects/longform/seed-demo/mix.yaml
PYTHONPATH=. $PY projects/longform/deliver.py \
  projects/longform/assets/seed-demo/renders/seed-demo.wav \
  examples/longform-seed/seed-demo.mp3 --gain -0.35
```

配布 mp3 は −16.34 LUFS・トゥルーピーク −1.03 dBTP・LRA 3.80 LU（`check_loudness.py` 合格）。
