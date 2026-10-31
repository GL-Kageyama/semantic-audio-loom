# 聞き比べ — 文末の記号だけを替える

`projects/longform/experiments/demos/punctuation-demo/` の 46.0 秒。語り手が札を読み、真白が同じ 1 行
（`明日、また来るね`）を、**最後の 1 文字だけ**替えて言う。Spec は 4 通りで共通
（neutral・natural・controlled・none）。seed は 1 と 3 の 2 本ずつ。

| 時刻 | 何 | seed | f0 | 長さ |
| --- | --- | --- | --- | --- |
| 0:01.4 | 導入「文の終わりだけを替えます。声が、どう変わるか」 | — | — | — |
| 0:09.1 | `。` | 1 | 326.0 Hz | 2.85 s |
| 0:12.2 | `。` | 3 | 290.4 Hz | 2.80 s |
| 0:18.3 | `？` | 1 | 333.6 Hz | 2.67 s |
| 0:21.2 | `？` | 3 | 306.8 Hz | 2.60 s |
| 0:26.7 | `！` | 1 | 359.6 Hz | 2.72 s |
| 0:29.7 | `！` | 3 | 341.4 Hz | 2.55 s |
| 0:35.2 | 記号なし | 1 | 320.4 Hz | 2.50 s |
| 0:38.2 | 記号なし | 3 | 260.2 Hz | 2.55 s |
| 0:41.7 | 結び「句読点は、間ではなく、高さを動かしました」 | — | — | — |

## 聴きどころ

- **`！` の 2 本が、いちばん高い**（359.6 / 341.4 Hz）。`？` も `。` より高い
  （+7.6 / +16.4 Hz）。**記号を変えるだけで、同じ seed の声が動く。**
- **記号なしの seed 3 がいちばん低い（260.2 Hz）**。句点を外すと語尾が落ちる
  （`experiments/punctuation/acting-punctuation/` の実測：語尾の傾き +4.5 → −21.5 半音/秒）。
- 長さはむしろ短くなる（2.85 → 2.50 s）。**句読点は間ではない。**

⚠️ 見本は `script.yaml` から組むので強度 0.5。実験（`experiments/punctuation/acting-punctuation/`）は
llm 解決の none の Spec（強度 0.4）で、値は少し違う。**向きは同じ**
（実験：`？` +16.3 Hz 5/5・`！` +39.3 Hz 5/5）。

## 作る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/experiments/demos/punctuation-demo
PYTHONPATH=. $PY projects/longform/assemble.py --dir projects/longform/experiments/demos/punctuation-demo
PYTHONPATH=. $PY projects/longform/check_render.py \
  projects/longform/assets/punctuation-demo/renders/punctuation-demo.wav \
  --mix projects/longform/experiments/demos/punctuation-demo/mix.yaml
PYTHONPATH=. $PY projects/longform/deliver.py \
  projects/longform/assets/punctuation-demo/renders/punctuation-demo.wav \
  examples/longform/punctuation/punctuation-demo.mp3 --gain -0.60
```

配布 mp3 は −16.27 LUFS・トゥルーピーク −1.31 dBTP・LRA 2.50 LU（`check_loudness.py` 合格）。
