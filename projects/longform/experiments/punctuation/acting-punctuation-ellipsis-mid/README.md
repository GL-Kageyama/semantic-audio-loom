# 途中の「…」は、間にならない——読点に化けて、行を 0.85 秒短くする

文末の `…` は消されて `なし` と同じ音になった（`experiments/punctuation/acting-punctuation-ellipsis/`）。
途中に置いたらどうなるか。「明日、……また来るね」の 5 本を焼き、同じ Spec・
同じ seed の `なし`（`明日、また来るね`・`experiments/punctuation/acting-punctuation/`）と比べる。
Spec は共通（`experiments/subtext/acting-subtext/llm-specs.json` の none＝neutral・0.5・controlled）。

    PYTHONPATH=. $PY projects/longform/experiments/punctuation/acting-punctuation-ellipsis-mid/run.py
    PYTHONPATH=. $PY projects/longform/experiments/punctuation/acting-punctuation-ellipsis-mid/run_literal.py
    PYTHONPATH=. $PY projects/longform/experiments/punctuation/acting-punctuation-ellipsis-mid/run_trunc.py
    PYTHONPATH=. $PY bin/act_probe.py --tsv …/voice/*.wav > probe.tsv

## まず、字面がどうなるか

`normalize_ellipsis()`（`semantic_audio_loom/text.py`）は文中の `…` を `、` に
置き換える。だから `明日、……また来るね` は phonemize に **`明日、、また来るね`**
として渡る。同じ字面を省略記号なしで焼くと（`run_literal.py`）、**seed 1・4・5 は
md5 まで一致**、seed 2・3 も差は RMS −75.9・−72.8 dBFS（0.004 未満）。
**`…` 自身は何も足していない。読点が増えただけ。**

## 測った値

値は 1 本ごとの f0 中央値を 5 本で平均したもの。差は seed ごとの対の平均
（括弧は符号数）。

| 行 | f0 | 長さ | 無音率 | 抑揚幅 |
| --- | --- | --- | --- | --- |
| `明日、また来るね`（なし） | 302.3 Hz | 2.918 s | 0.315 | 8.72 半音 |
| `明日、……また来るね` | 305.0 Hz | **2.073** | **0.195** | 7.24 |

| 差 | 量 | 符号 |
| --- | --- | --- |
| 長さ | **−0.845 s** | 0/5 |
| 無音率 | −0.122 | 0/5 |
| f0 | +2.7 Hz | 3/5 |
| 抑揚幅 | −1.48 半音 | 1/5（上がった側） |
| 有声の割合 | −0.031 | 1/5 |

## 読み方

- **間は増えない。むしろ 0.85 秒縮む。** 無音率も 0.315 → 0.195 に下がる。
  `…` で「言いよどみ」を書くと、**間が入るのではなく、行が速くなる**。
- **後ろの節は読まれている。** 1.2 秒より後の 50 ms 窓にも声がある
  （5 本とも −13〜−17 dB）。頭だけを読んで切ったのではない。頭だけの行
  （`明日、` / `明日、、`・`run_trunc.py`）は 1.70〜1.90 秒だが、声は 0.1〜0.2 秒ぶん
  しかない（有声の割合 0.07〜0.12）。**2.07 秒の 5 本は、最後まで速く読んでいる。**
- f0 はほぼ動かない（+2.7 Hz・3/5）。抑揚幅は 4/5 で下がるが、速く読んだぶんか
  どうかは分けていない。
- ⚠️ 1 行・1 声・seed 5 本。**確かめたのは「`…` は読点になる」「行は短くなる」
  まで**で、速くなる機序は測っていない。

## 台本への含み

言いよどみを `…` で書いても、声は言いよどまない。文末なら消され、途中なら
読点に化けて行を縮める。**間は `pause_before`（台本の欄）で作る。**
読点を 1 個増やすのと同じことになるので、`experiments/punctuation/acting-notation/` の
「読点 1 個で f0 −17.0 Hz」も一緒に効く（この行では f0 は動かなかったが、
測った行が違う）。

耳で確かめる見本：`projects/longform/experiments/demos/ellipsis-demo/`（`examples/longform/ellipsis/`・
33.6 秒）。文末 2 本（同じ音）と、途中の `…` の 1 本（1.95 秒）を並べている。
