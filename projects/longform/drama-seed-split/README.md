# 人物の区別を seed で作れるか — ニジだけ seed 2 にした 89 本

出荷した演劇は**真白もニジも seed 1**。二人の声を分けているのは参照音声
（`mashiro` / `niji`）と、ミックスの帯域（ニジは電話の帯域）で、seed ではない。
**seed を人物ごとに振るのは、分離を増やす正しい道具か**を、脚本をそのまま使って
ニジの 42 本だけ seed 2 で作り直して測った（`script.yaml` は `drama/` と同じで、
ニジの seed が 2 のだけが違う）。

## f0 の中央値（作品の段・89 本）

| 人物 | 出荷版（seed 1） | ニジだけ seed 2 | 差 |
| --- | --- | --- | --- |
| 真白 | 303.4 Hz | 301.7 Hz | — |
| ニジ | 315.6 Hz | **294.1 Hz** | **−21.5 Hz**（39/42 が下降・p = 8e−10） |
| 二人の差（ニジ − 真白） | **+12.2 Hz** | **−7.6 Hz** | 符号が反転 |

- **seed を 1 つ動かすと、人物の差より大きい**（ニジの平均 −21.5 Hz 対 二人の差 12.2 Hz）。
  1 本ずつでは −77.6〜+8.3 Hz に散る（`y10` が −77.6・`s36` が −66.9）。
- **分離は広がらず、縮んだ。** ニジのほうが真白より低い側へ回り、二人の差は
  12 Hz から 7.6 Hz へ（符号も反転）。**seed は「どちらへ動くか」を選べない。**
- 長さも +0.19 秒動く（1 本あたり最大 0.48 秒）。**作品の尺・間は seed で動く。**
- 真白の差（平均 −1.6 Hz）は seed の話ではない。**基準線に入っている古い take のせい**で、
  内訳の大半は `s70` 1 本（329.7 → 242.1 Hz・−87.6 Hz）。残り 5 本は −1.8〜−5.0 Hz
  （`HISTORY.md`「出荷した声 10 本が、台本より古かった」）。

## 何が言えるか

- **人物の分離を seed で作らない。** 参照音声と `voice_fx` の帯域が分離の道具で、
  seed は**動くが向きを選べない揺らぎ**（`emotion-seed/` の「seed の幅 84.6 Hz」と同じ性質）。
- seed を人物に固定する意味はある（同じ人物の take どうしが揃う）。**だが「二人を離す」
  ために片方の seed を動かすと、離れる保証は無い。**
- ⚠️ この比較の真白側は、作り直す前の 6 本（breathiness 以前）を含む基準線
  （`drama-level/levels.tsv`）と比べている。**ニジ側（42 本）は 1 本も変わっていない**
  ので、ニジの −21.5 Hz は seed の効果として読める。

## 限界

- **seed 1 → 2 の 1 組だけ。** seed 3 以降は試していない。
- f0 の中央値だけで見ている。**声質（スペクトル）の分離は測っていない。**
- ニジの声はミックスで電話の帯域を掛ける（`drama/voice_fx.yaml`）。ここで測ったのは
  **帯域を掛ける前**の声。
- 古い take が混ざった基準線（真白 303.4 Hz）に対し、作り直した真白は 301.7 Hz。
  差の大半は `s70` 1 本。

## 測る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/drama-seed-split
PYTHONPATH=. $PY bin/act_probe.py --tsv projects/longform/assets/drama-seed-split/voice/*.wav \
  > projects/longform/drama-seed-split/probe.tsv
PYTHONPATH=. $PY projects/longform/check_script_sync.py --dir projects/longform/drama-seed-split
```
