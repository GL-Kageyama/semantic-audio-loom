# 聞き比べ — 声を変えるのは、どの欄か

同じ一言（「明日、また来るね。」）・同じ seed（2）で、**速さ（speed）5 語**と
**演技の型（delivery）3 語**だけを振って並べた 69 秒の見本。語り手が札を読み、
真白が毎回同じ台詞を言う。

強度の段は [examples/longform-intensity/](../longform-intensity/) に別の見本がある。

## 並び

| 秒 | 中身 | 長さ | f0 |
| --- | --- | --- | --- |
| 0:01.4 | 導入（語り手） | — | — |
| 0:10.3 | とても、おそく（very_slow） | **4.35 s** | 295.5 Hz |
| 0:16.7 | おそく（slow） | 3.55 s | 298.9 Hz |
| 0:22.5 | ふつう（natural） | 3.02 s | 302.4 Hz |
| 0:27.3 | はやく（fast） | 2.75 s | 304.1 Hz |
| 0:32.5 | とても、はやく（very_fast） | **2.30 s** | 313.0 Hz |
| 0:43.4 | やさしく（gentle） | 3.10 s | 305.9 Hz |
| 0:48.3 | 平らに（flat） | 2.90 s | **289.6 Hz** |
| 0:53.4 | 冷たく（cold） | 2.92 s | 298.9 Hz |

## 聴きどころ

- **速さの 5 本は、5 つとも違う。** 4.35 → 2.30 秒（1.89 倍）。5 seed の平均でも
  1.80 倍で、**5 seed それぞれの中で順序が崩れない唯一の欄**。
- **やさしく と 平ら は、はっきり違う**（−16 Hz・−0.2 秒）。
- **やさしく と 冷たく は、近い**（−7 Hz）。5 seed の平均では cold −9.4・flat −18.4 Hz で、
  **flat だけが「別の声」**、cold はその半分。
- この見本に入れていない欄の話：**明るく・ためらい・抑えて**は、やさしく と ±2 Hz で
  同じになる（[projects/longform/acting-delivery/](../../projects/longform/acting-delivery/)）。
  **声量（whisper / loud）は声そのものを変えない**（energy 0.08 dB）。作品の中で声量が
  変わるのは、組み立てのときに `gain_db` を掛けているから。

## 測ったこと

| 欄 | 語 | 声に届く段 | 出どころ |
| --- | --- | --- | --- |
| speed | 5 | **5**（単調・1.80 倍） | `acting-speed/` |
| delivery | 12 | 2（flat・cold のみ） | `acting-delivery/` |
| volume | 5 | 0（声としては） | `acting-volume/` |
| intensity | 5 | 2 | `acting-intensity/` |

詳しくは [projects/longform/REPORT.md](../../projects/longform/REPORT.md) の
「Direction の欄は、どれが段になるか」。

## 作る

```zsh
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/knob-demo
PYTHONPATH=. $PY projects/longform/assemble.py --dir projects/longform/knob-demo
PYTHONPATH=. $PY projects/longform/deliver.py \
  projects/longform/assets/knob-demo/renders/knob-demo.wav \
  examples/longform-knobs/knob-demo.mp3 --gain -0.56
```

## 限界

- **1 行・1 seed（2）。** 5 seed の平均は上の表のとおりだが、この見本の声の高さは
  seed 2 の値。
- 速さの差は長さで測っている。**長い台詞では、同じ比になるとは限らない。**
- 配布の高さは −1 dBTP を優先している（mp3 で I −17.1 LUFS・TP −1.25 dBTP）。
  −16 LUFS には届かない。
