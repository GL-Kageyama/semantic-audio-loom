# seed-voices — seed の癖は、声をまたぐか

`experiments/analysis/emotion-seed/` で「高さは seed が決める」と分かったが、それは真白 1 人での話だった。
ライブラリの 4 つの声（narrator / mashiro / niji / gozen-niji-katari）で同じ 1 行を
seed 1〜3 ずつ作る（12 本）。設定は全部そろえる。

## 結果 — seed の癖は 4 つの声で同じ向き

**seed 1 がいちばん高く、seed 2・3 は低い。4 つの声すべてで。**

| 声 | 平均 f0 | s1−平均 | s2−平均 | s3−平均 | 幅 |
| --- | --- | --- | --- | --- | --- |
| narrator（語り手） | 253.4 Hz | +17.6 | −3.5 | −14.1 | 31.7 Hz |
| mashiro（真白） | 299.0 | +27.0 | −18.5 | −8.6 | 45.5 Hz |
| niji（ニジ） | 314.1 | +21.4 | −18.6 | −2.9 | 40.0 Hz |
| katari（午前二時の語り） | 291.6 | +26.9 | −19.1 | −7.8 | 46.0 Hz |

- **符号は 4 声とも「＋ − −」。** ずれの相関は 0.74〜1.00（mashiro–katari は 1.00）。
  **seed の癖は、声ごとの偶然ではなく、器（参照）をまたぐ共通の癖。**
- **大きさは声で違う**（幅 31.7〜46.0 Hz）。「seed を替えると 40 Hz 動く」は、
  この 4 声の中の幅であって、すべての参照の幅ではない。
- narrator は energy も seed で 5.9 dB 動く（−17.3 → −23.2）。**高さだけの癖ではない。**

## 音色 — seed は「人物を替える」のと同じだけ動かす

MFCC（有声フレーム）で、同じ声の中で seed を替えた距離と、声どうしの距離。

| | 距離 |
| --- | --- |
| 同じ声で seed を替える | narrator 24.5 / mashiro 17.1 / niji 12.8 / katari 14.7 |
| mashiro ↔ niji ↔ katari（重心） | 13.0〜13.5 |
| narrator ↔ その 3 声 | 63.4〜68.7 |

- **近い 3 声（真白・ニジ・午前二時の語り）のあいだの距離（13.0〜13.5）は、同じ声で
  seed を替える距離（12.8〜17.1）と同じ大きさ。** つまり **seed を固定しないと、
  「誰が話しているか」と「どの seed か」が同じ大きさで混ざる。**
- 演劇が人物を帯域（ニジ +3 dB・320–3400 Hz）で分けているのは、この距離を
  作るため。声そのものの距離は 13 しかない。

## 限界

- 4 声・1 行・3 seed。**参照音声の数だけ声が増やせるが、ここでは 4 つだけ。**
- ライブラリの 3 声（mashiro・niji・katari）は互いに近い（13 前後）。**別の声を足せば、
  声どうしの距離の分布は変わる。**
- 台詞は「明日、また来るね。」1 行。`experiments/analysis/emotion-seed/` で行によって seed の振れ幅が
  49 → 83 Hz と変わったので、**行を替えれば幅は動く。**

## 作る・測る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/experiments/voice/seed-voices
PYTHONPATH=. $PY projects/longform/experiments/voice/seed-voices/measure_seed_voices.py
```
