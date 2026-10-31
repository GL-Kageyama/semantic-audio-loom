# 読点は、間にならない

`prosody.pauses`（LLM が書いてくる「明日のあと 0.3 秒」）は散文に入らない
（Provider に構造化制御が無い）。代わりに台詞へ読点を足せば間になるかを測った。

- 台詞「明日、また来るね。」の「明日」のあとに読点を **1 / 2 / 3 個**置く。
- 同じ Spec（`acting-subtext/llm-specs.json` の `none`・`beta` 0.7）× seed 1〜5 = **15 本**
  （`run.py`・`probe.tsv`）。
- 2 個は「……（ためらう）」を書いたときに `normalize_ellipsis` が出す形でもある
  （文中の「…」→「、」）。

## 結果：増えない。3 個では縮む

| 台詞 | 長さ（seed 1〜5・秒） | 平均 | 1 個からの差 |
| --- | --- | --- | --- |
| 明日、また来るね。 | 2.85 / 3.02 / 2.82 / 3.37 / 3.37 | **3.088** | — |
| 明日、、また来るね。 | 2.85 / 3.00 / 2.87 / 3.42 / 3.32 | **3.093** | **+0.005 秒**（2/5） |
| 明日、、、また来るね。 | 2.57 / 2.87 / 2.67 / 3.05 / 3.30 | **2.893** | **−0.195 秒**（0/5） |

- **2 個にしても長さは変わらない**（+5 ms）。間の比だけ **+0.026（5/5）** 上がるので、
  同じ長さの中で有声がわずかに減る（聞いて分かる差ではない）。
- **3 個では 5 本とも短くなる**（−0.195 秒）。**読点を増やすと縮む。**
- よって `pauses` を読点で代用する道は無い。**間は組み立て（`pause_before`）で作る**
  ——`projects/longform/assemble.py` が既にそうしている。

## 何が言えるか

- 生成の側で**間を指定する手段は無い**（`prosody.pauses` は散文に入らず、読点は効かない）。
  間は台本の側（`script.yaml` の `pause_before`）と組み立てで作る。
- 「…」を「、」に正規化するのは**「へぇ」に化けるのを避けるため**で、ためらいの間を
  作るためではない（[HISTORY](../../../HISTORY.md) の 2026-08-30）。この 15 本は、
  その置換が作る「、、」の形が**間にもならない**ことを見ている。

## 測る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/acting-pauses/run.py
PYTHONPATH=. $PY bin/act_probe.py --tsv projects/longform/assets/acting-pauses/voice/*.wav
```

素材は `projects/longform/assets/acting-pauses/voice/`（追わない・焼き直せる）。
