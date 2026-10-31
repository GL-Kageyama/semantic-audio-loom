# 強い欄どうし（speed と pitch）は、足し算にならない

`speed` と `pitch` は、どちらも f0 を動かす。前の節では**弱い欄**（`delivery`）が
速さの端で埋まった。では**強い欄どうし**を同時に振ると、足されるのか。
同じ行・joy・moderate・`delivery` controlled・breathiness none・seed 1〜10 で
`speed` 2 段 × `pitch` 3 語の 60 本。

| speed | pitch | f0 (Hz) | 長さ (s) |
| --- | --- | --- | --- |
| natural | low | 302.0 | 3.26 |
| natural | natural | 315.5 | 3.09 |
| natural | high | 315.4 | 3.11 |
| very_fast | low | 302.5 | 2.50 |
| very_fast | natural | 319.8 | 2.46 |
| very_fast | high | 321.4 | 2.42 |

## pitch の効きは、下だけ

| 条件 | low − natural | high − natural |
| --- | --- | --- |
| speed natural | **−13.5 Hz**（9/10 が下・p = 0.0002） | −0.1 Hz（1/10・p = 0.87） |
| speed very_fast | **−17.3 Hz**（10/10 が下・p = 0.0035） | +1.6 Hz（4/10・p = 0.37） |

- **`low` は効く。`high` は効かない**（この条件では 0.1 Hz）。
  `acting-knob-stack-pitch/`（gentle）では high が +2.9 Hz だったので、
  **high の効きは ±3 Hz のあいだで揺れる**——段として当てにしない。
- ⚠️ **`low` も、seed 5 本では向きが揃わなかった**（−10.8 Hz・下がったのは 4/5・p = 0.026）。
  seed 10 本にすると 9/10 に揃う。**「効かない」と読む前に、seed を増やす。**

## speed の高さの効きは、pitch が低いと消える

| pitch | very_fast − natural（f0） | 同符号 |
| --- | --- | --- |
| low | **+0.5 Hz**（p = 0.91） | 8/10 |
| natural | +4.3 Hz（p = 0.053） | 6/10 |
| high | **+5.9 Hz**（p = 0.034） | 8/10 |

- **低い声では、速くしても高くならない。** 高い声では速さが効く。
- 加算からのずれは low −3.8 Hz・high +1.7 Hz。**どちらも有意でない**（p ≥ 0.35）。
  つまり「足し算」とも「埋まる」とも、この n では言えない。
  **言えるのは「pitch が低い側では、速さの高さの効きが見えない」まで。**
- ⚠️ ここでの速さの効き（+4〜+6 Hz）は、**natural → very_fast** の差。
  両端（very_slow → very_fast）なら +14.8〜17 Hz（`acting-speed/`）なので、
  **同じ欄でも、どの 2 点を比べるかで数が変わる。**

## 長さは、pitch が何であっても同じだけ縮む

- very_fast − natural の長さは low −0.76 / natural −0.62 / high −0.69 秒で、
  **すべて 10/10・p ≤ 1.1e−08。**
- **強い欄（速さ→長さ）は、別の欄と重ねても減らない。** 弱い欄（delivery→f0）が
  速さの端で消えたのと対照的。

## 限界

- 1 行・1 人物（mashiro）・1 感情（joy）・`delivery` controlled・beta 0.7。
- pitch は 3 語（low / natural / high）だけ。6 語のうち測っていない 3 語は残っている。
- 交互作用の推定は幅が広い（low の標準誤差 4.4 Hz）。**「無い」と言えるのは
  ±10 Hz より大きい交互作用まで。**

## 測る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/acting-knob-stack-speed-pitch
PYTHONPATH=. $PY bin/act_probe.py --tsv projects/longform/assets/acting-knob-stack-speed-pitch/voice/*.wav \
  > projects/longform/acting-knob-stack-speed-pitch/probe.tsv
PYTHONPATH=. $PY projects/longform/check_script_sync.py --dir projects/longform/acting-knob-stack-speed-pitch
```
