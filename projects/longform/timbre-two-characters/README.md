# timbre-two-characters — 二人の声は、声そのもので分かれるか

同じ台詞を真白とニジに喋らせ、**有声フレームの距離**で「同一人物（seed 違い）」と
「別人（同じ台詞・同じ seed）」を比べる。既定の混ぜ方（`beta` 0.7・`alpha` 0.35）。

| ファイル | 中身 |
| --- | --- |
| `script.yaml` | 3 台詞 × 2 人物 × seed 1〜3＝18 キューの定義 |
| `probe.tsv` | `bin/act_probe.py` の測定（f0・速さ・間・張りなど） |
| `measure_two.py` | 同一人物と別人の距離を出す |

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/timbre-two-characters
PYTHONPATH=. $PY projects/longform/timbre-two-characters/measure_two.py
```

距離の計器は `../measure_timbre.py`（有声フレームだけ。無音の割合を混ぜない。
`../check_timbre_metric.py` で欠陥と修理を確かめられる）。

## 結果

| 比較 | 組 | 距離（中央値） | 範囲 |
| --- | --- | --- | --- |
| 同一人物（同じ台詞・seed 違い） | 18 | 16.4 | 9.9–30.4 |
| 別人（同じ台詞・同じ seed） | 9 | 13.8 | 9.6–31.6 |

**別人のほうが近い。** 声そのものでは二人を聞き分けられない。作品で分けているのは
ニジの電話帯域（`examples/longform-drama/voice_fx.yaml`）。包絡の距離は
1.95 → 9.60 dB になる。

読み取りは `../REPORT.md` の「声は分けられるか（P4）」。
