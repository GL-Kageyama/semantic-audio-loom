# intonation の残り 2 語（neutral / wavering）

`intonation` の 5 語のうち、`experiments/pitch/acting-inton-070/` が測っていなかった neutral と
wavering を、**同じ条件**（「明日、また来るね。」・neutral・controlled・beta 0.7・
seed 1〜5）で作った 10 本。**5 語を並べた結論は `experiments/pitch/acting-inton-070/README.md`。**

| intonation | f0 (Hz) | 語尾の傾き (st/s・中央値) |
| --- | --- | --- |
| neutral | 290.3 | 2.71 |
| wavering | 291.4 | 3.18 |

- **2 語の差は +1.1 Hz（2/5・p = 0.21）。** 語尾の傾きも差なし（3/5・p = 0.35）。
- seed 2・5 では neutral と wavering が **同じ値**（280.5 / 241.4 Hz）。
  **この 2 つの seed では、語が捨てられている。**

## 測る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/experiments/pitch/acting-intonation2
PYTHONPATH=. $PY bin/act_probe.py --tsv projects/longform/assets/acting-intonation2/voice/*.wav \
  > projects/longform/experiments/pitch/acting-intonation2/probe.tsv
```
