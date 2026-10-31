# 感情に「型」を足しても、隣どうしは離れない（むしろ入れ替わる）

`experiments/basics/acting-emotion-ladder/` では、隣り合う 2 語（fear と joy）が **+1.6 Hz** で区別できなかった。
`delivery` は 1 語で −18〜+7 Hz 動く欄なので、**型を足せば離れるのか**を測った。
neutral / joy / fear × gentle / aggressive / cold × seed 1〜5 = **45 本**（同じ行・
moderate・speed natural・breathiness none・beta 0.7）。

| emotion | gentle | aggressive | cold |
| --- | --- | --- | --- |
| neutral | 298.4 | 298.5 | 288.3 |
| joy | 318.6 | **325.3** | 309.2 |
| fear | **321.4** | 318.3 | 312.2 |

## fear − joy は、どの型でも 3 Hz 以下（aggressive では逆になる）

| delivery | fear − joy | 中央値 | 同符号 | p |
| --- | --- | --- | --- | --- |
| gentle | +2.8 Hz | +3.7 | 4/5 | 0.063 |
| cold | +3.1 Hz | +3.9 | 4/5 | 0.10 |
| **aggressive** | **−7.0 Hz** | −8.3 | **0/5** | **0.015** |

- **型を足しても、離れない。** gentle・cold は 3 Hz で、seed の散らばり（9 セルの
  幅 84.1〜101.6 Hz）の中。p も 0.06・0.10 で有意でない。
- ⛔ **aggressive では、向きが逆になる。** fear が joy より **7.0 Hz 低い**（5 seed すべて）。
  **「強く言う」は喜びを上げ、恐怖を下げる**——感情と型が打ち消し合う。

## 感情の効きは、型をまたいでも残る

- joy − neutral は gentle +20.2・aggressive +26.8・cold +20.9 Hz（**すべて 5/5**）。
- fear − neutral は gentle +23.0・aggressive +19.7・cold +24.0 Hz（**すべて 5/5**）。
- **neutral との差（+20〜+27 Hz）は、型を替えても消えない。**
  消えるのは**隣どうしの差**（3 Hz）だけ。

## 型の効きは、感情で変わる

| emotion | aggressive − gentle | cold − gentle |
| --- | --- | --- |
| neutral | **+0.1 Hz**（2/5・p = 0.91） | −10.1 Hz（0/5・p = 0.0058） |
| joy | **+6.7 Hz**（5/5・p = 0.0085） | −9.4 Hz（1/5・p = 0.033） |
| fear | **−3.1 Hz**（0/5・p = 0.012） | −9.2 Hz（0/5・p = 0.0067） |

- **`aggressive` は neutral には効かない**（+0.1）。**喜びでだけ効く**（+6.7）。
  ⚠️ この +6.7 は `experiments/basics/acting-knob-stack-pitch/` の joy の値（+6.68）と一致する。
- **`cold` はどの感情でも −9〜−10 Hz**。**並びを変えない下げ**——だから区別には使えない。
- **型は感情の上に足されるのではなく、感情ごとに別の向きへ働く。**

## 何が言えるか

- **感情の書き分けを、型で救うことはできない。** 隣どうしは 3 Hz のままで、
  `aggressive` を使うと**逆転する**。
- **書き分けたいなら、感情の語ではなく `speed` を使う**（1.74〜1.80 倍・5/5 単調）。
- **neutral からの差は、型を替えても読める**（+20〜+27 Hz・全条件 5/5）。
  「この人は今、感情が高い」は言える。「何の感情か」は言えない。

## 限界

- 1 行・1 人物（mashiro）・beta 0.7・seed 5 本。
- 感情は 3 語（neutral / joy / fear）だけ。**fear と joy は、11 語の中で最も近い組**。
- 測ったのは f0 中央値だけ。長さ・抑揚・張りは見ていない。

## 測る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/experiments/basics/acting-emotion-delivery
PYTHONPATH=. $PY bin/act_probe.py --tsv projects/longform/assets/acting-emotion-delivery/voice/*.wav \
  > projects/longform/experiments/basics/acting-emotion-delivery/probe.tsv
PYTHONPATH=. $PY projects/longform/check_script_sync.py --dir projects/longform/experiments/basics/acting-emotion-delivery
```
