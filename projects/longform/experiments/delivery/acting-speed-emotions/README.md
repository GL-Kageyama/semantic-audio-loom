# 速さの 5 段は、感情を替えても 5 段

`experiments/delivery/acting-speed/` は joy だけで測っている。台本を書く人に渡す助言は「声を動かしたいなら
`speed` を使え」なので、**別の感情でも同じ順序になるか**を確かめた。
anger / sadness × 5 語 × seed 5・50 本。台詞・キャラ・他の欄は `experiments/delivery/acting-speed/` と同じ
（mashiro・「明日、また来るね。」・intensity moderate・volume normal・delivery controlled）。

## 長さ（秒・seed 5 の平均）

| 速さ | anger | sadness | joy（`experiments/delivery/acting-speed/`） |
| --- | --- | --- | --- |
| very_slow | 4.35 | 4.20 | 4.39 |
| slow | 3.58 | 3.59 | 3.59 |
| natural | 3.18 | 3.25 | 3.06 |
| fast | 2.90 | 2.90 | 2.84 |
| very_fast | **2.43** | **2.42** | 2.44 |
| 比（very_slow ÷ very_fast） | **1.79** | **1.74** | 1.80 |

| 段の間 | anger | sadness |
| --- | --- | --- |
| very_slow → slow | −0.77 s（5/5・p = 5.9e−06） | −0.62 s（5/5・p = 6.8e−05） |
| slow → natural | −0.40 s（5/5・p = 1.5e−04） | −0.34 s（5/5・p = 3.1e−04） |
| natural → fast | −0.28 s（5/5・p = 3.2e−04） | −0.35 s（5/5・p = 7.5e−05） |
| fast → very_fast | −0.47 s（5/5・p = 9.4e−07） | −0.48 s（5/5・p = 8.6e−07） |

## 何が言えるか

- **3 感情とも、seed 5 のすべてで 5 語が単調に短くなる（5/5）。** 段の比も 1.74〜1.80 で
  そろう。**`speed` だけが、感情を替えても崩れない欄。**
- **伸び縮みするのは、発話そのもの。** 無音の割合は 0.22〜0.32 で段によって動かないので、
  `very_slow` と `very_fast` の差は間の詰め方では説明できない。発話時間は
  anger 3.35 → 1.90 秒（1.76 倍）、sadness 3.18 → 1.81 秒（1.76 倍）。
- **速さは高さを運ばない。** f0 の中央値は anger 305.6 / 305.3 / 310.0 / 309.9 / 316.1、
  sadness 300.6 / 295.2 / 294.4 / 306.3 / 295.8 で、**どちらも単調でない**。
  joy の見本（`knob-demo`）では速いほうが 17 Hz 高く出たが、それは seed 1 つの
  偶然として扱う（ここは 5 seed の平均）。
- energy も動かない（−15.2〜−13.9 dB・段でばらつき、単調でない）。

## 限界

- **1 行・2 感情を足しただけ**（joy と合わせて 3 感情）。anger と sadness 以外は未測。
- 速さを長さで測っている。長い台詞で同じ比になるかは未測（`acting-longline` は強度の話）。
- seed 5 のうち 3 感情 × 5 段 × 5 seed = 75 本を測ったが、長さの比は「この一言」のもの。

## 測る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/experiments/delivery/acting-speed-emotions
PYTHONPATH=. $PY bin/act_probe.py --tsv projects/longform/assets/acting-speed-emotions/voice/*.wav \
  > projects/longform/experiments/delivery/acting-speed-emotions/probe.tsv
```
