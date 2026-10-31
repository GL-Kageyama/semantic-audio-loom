# speed だけが、5 語とも段になる

強度は 2 段（`experiments/intensity/acting-intensity/`）、声量は 0 段（`experiments/delivery/acting-volume/`）、delivery は 3 段
（`experiments/delivery/acting-delivery/`）。**`speed` は 5 語が 5 段のまま、単調に効く。**

## 同じ行・同じ感情で、speed だけを振る

1 行「明日、また来るね。」・mashiro・joy・moderate・volume normal・delivery controlled・
seed 1〜5。`speed` を 5 語に振った 25 本（`script.yaml`）。

| speed | 長さ (s) | natural との差 | 同符号 | p | 速さ（拍/秒） |
| --- | --- | --- | --- | --- | --- |
| very_slow | 4.39 | **+1.33** | 5/5 | 0.00002 | 5.08 |
| slow | 3.59 | +0.52 | 5/5 | 0.0001 | 5.10 |
| natural | 3.06 | — | — | — | 5.60 |
| fast | 2.84 | −0.23 | 0/5 | 0.0010 | 5.32 |
| very_fast | 2.44 | **−0.63** | 0/5 | 0.00004 | 5.76 |

- **5 語が単調に並ぶ**（4.39 → 3.06 → 2.44 秒）。**両端の比は 1.80 倍。**
- **5 seed すべてが同じ向き**（very_slow・slow は 5/5 伸び、fast・very_fast は 5/5 縮む）。
  符号がそろうのは、ここまで測った欄では speed だけ。
- 一部の seed で伸びが大きい（very_slow は seed 4・5 が 4.85・4.70 秒）が、
  **5 seed それぞれの中でも 5 語の順序が完全に単調**（25 本・逆転した組は無し）。
- 無音の割合は 0.22〜0.27 で、速さと並ばない。**速さは「間」ではなく発話そのものが
  伸び縮みしている**（この行に長い間が無いため）。
- 速さの推定値（`rate_mora_s`）は 5.08〜5.76 で、長さほどきれいに動かない
  （slow p = 0.012・fast p = 0.15）。**伸ばすと拍の数え方も変わるので、
  長さで読むほうが確か。**
- **高さも両端で開く。** f0 の 5 段の平均は 306.0 → 312.6 → 314.2 → 319.5 → 320.8 Hz。
  **very_slow と very_fast で +14.8 Hz**（seed ごとでは 4/5）。段の途中は単調でない。
  **速くすると高くなる**——「長さだけの欄」ではない。⚠️ **長い行（24 文字）では
  この開きは出ない**（`experiments/delivery/acting-speed-longline/` は 285.2 → 284.5 Hz）。**行の長さで変わる。**
- **delivery を替えても、開きかたは同じ**（`experiments/basics/acting-knob-stack/`）。very_slow → very_fast は
  gentle −1.95 秒（1.79 倍）・aggressive −1.88 秒（1.76 倍）で、どちらも 0/5。

## 何が言えるか

- **演じ分けの土台になるのは speed。** 方向の語が素直に段になる欄は、いまのところ
  これと `pitch` だけ（`experiments/pitch/acting-pitch/` は high だけが natural から +19 Hz 離れる）。
- 台本はすでにこれを一番使っている（演劇 89 本のうち slow 44・natural 31・fast 10・
  very_slow 4）。**意図した強弱が実際に届いている欄は、ここだけ。**

## 限界

- 1 行・1 人物・1 感情（joy）。**anger と sadness を足すと 5 seed とも同じ順序で、
  比は 1.74・1.79 倍**（`experiments/delivery/acting-speed-emotions/`）。**長い行（24 文字）では 1.75 倍・
  5/5 単調**（`experiments/delivery/acting-speed-longline/`）。
- very_fast の 2.44 秒は、この行（14 拍）での値。**秒ではなく比で読むこと。**
- 長さは「間」と「発話」の両方を含む。この行では `pause_ratio` が動かなかったので、
  動いたのは発話の側。**間の多い台詞では、同じ長さの伸びでも中身が違いうる。**

## 測る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/experiments/delivery/acting-speed
PYTHONPATH=. $PY bin/act_probe.py --tsv projects/longform/assets/acting-speed/voice/*.wav \
  > projects/longform/experiments/delivery/acting-speed/probe.tsv
```
