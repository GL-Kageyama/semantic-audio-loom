# 表に無い自由文は、声を動かすか

`_spec_prompt` は固定の語表（emotion / delivery / 強度 / 速さ / pitch / 抑揚）から
散文を組む。**表に無い一文を足したら声は動くか**を測った。

- 台詞「明日、また来るね。」・真白・同じ Spec（`acting-subtext/llm-specs.json` の
  `none`・`beta` 0.7）に、**散文を 1 文だけ足す**。
- 足す文：なし / `She is holding back tears.` / `She is furious but hiding it.` /
  `She is smiling as she says it.` / `She is afraid of the answer.`
- × seed 1〜5 = **25 本**（`run.py`）。散文はこの 5 通りで、ほかの欄はすべて同じ。

## 結果：動くが、seed の 2% しかない

`probe.tsv` の f0 中央値。基準（`none`）からの差：

| 足した文 | f0（seed 1〜5・Hz） | 平均差 | 向き |
| --- | --- | --- | --- |
| （なし） | 333.6 / 285.4 / 297.2 / 324.1 / 245.6 | — | — |
| 涙をこらえている | 335.5 / 287.1 / 298.9 / 326.0 / 247.0 | **+1.72 Hz** | 5/5 |
| 怒っているが隠している | 335.5 / 288.7 / 298.9 / 322.2 / 245.6 | **+1.00 Hz** | 3/5 |
| 笑いながら言っている | 333.6 / 285.4 / 297.2 / 321.3 / 244.2 | **−0.84 Hz** | 0/5 |
| 返事が怖い | 335.5 / 287.1 / 300.6 / 326.0 / 247.0 | **+2.06 Hz** | 5/5 |

- **いちばん大きい「返事が怖い」でも +2.1 Hz**。この 25 本の seed の散らばりは
  **244.2〜335.5 Hz（91.3 Hz）**で、2.1 Hz はその **2%**。
- 14 欄のうち、ほかに揃った動きは「返事が怖い」の語尾の傾き **+2.7 半音（4/5）**と
  間の比 +0.008（4/5）だけ。**張り（energy）も速さも息も動かない。**
- 散文は `Kotodama_Prompter` に渡るだけで、seed ごとに変わるのは拡散のノイズの側。
  よって**同じ散文なら 5 seed の差はノイズ**で、上の 1〜2 Hz はその中でも揃った側。

## 何が言えるか

- **感情を書いた散文は、このモデルでは演技にならない。** 効いているのは表の語
  （`delivery` の 4 語・強度の段・速さの 5 語）で、**表に無い語彙を足しても増えない**。
- `acting-subtext/` の結論（llm が subtext を散文にしても、効くのは `intensity` の段だけ）
  と**同じ向き**。**上限は表ではなくモデルの側**にある。
- ⚠️ ここで試したのは**感情の記述**だけ。音の記述（`whispering`・`very slow`）は
  表に既にあり、そちらは効く（`volume` の `shout`・`speed` の 5 語）。

## 測る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/acting-freetext/run.py
PYTHONPATH=. $PY bin/act_probe.py --tsv projects/longform/assets/acting-freetext/voice/*.wav
```

素材は `projects/longform/assets/acting-freetext/voice/`（追わない・焼き直せる）。
