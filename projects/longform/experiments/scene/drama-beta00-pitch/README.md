# drama-beta00-pitch — 床の芝居に `pitch` を振った版

[床の `drama-beta00`](../drama-beta00) の 89 キューに、`pitch` を人物ごとに足しただけの版。
真白 `very_low`（47 本）・ニジ `high`（42 本）。台詞・seed・間・`beta` 0.0・効果音・帯域は同じ。

8 行の聞き比べ（`floor-two-speakers`）で 12/12 だった「ニジが上」が、作品 89 本でも
成り立つかを見るための版。**聞き比べと実測は**
[examples/longform/drama-pitch/](../../../../../examples/longform/drama-pitch)。

## 要点（測った値）

| 項目 | beta00 | beta00-pitch |
| --- | --- | --- |
| 尺（組み上げ後） | 339.1 秒（門 合格） | **291.0 秒（門 未達・5 分に 9 秒足りない）** |
| 生の声の合計 | 真白 134.1 / ニジ 137.5 秒 | **真白 89.0** / ニジ 139.2 秒 |
| f0 の中央値 | 311.2 / 316.7 Hz | 295.5 / 318.5 Hz |
| 感情の偏りを除いた差（真白 − ニジ） | +0.06 Hz | **−13.38 Hz** |
| 感情 8 種の平均 f0 の幅 | 79.1 Hz | 69.5 Hz |
| 抑揚（8 感情の平均・半音） | 7.40 | 6.20（真白 7.08 → 4.93） |
| ニジが隣の真白より上のキュー | 21/42 | 31/42 |

`pitch` は DSP のノブではなく、プロバイダに渡す散文の一文（`with a very low pitch`）。
`very_low` は真白の台詞を 3 割短くし、起伏を潰す。ニジの `high` はほとんど何も変えない
（2 人の長さの比の中央値：真白 0.639 / ニジ 1.01）。

短縮は**長いテイクに集中する**：1 キューあたりの中央値で、囁き −2.30 秒・quiet −1.34・
normal −0.46、very_slow −1.69・slow −1.35・natural −0.28。

## 置いてあるファイル

| ファイル | 中身 |
| --- | --- |
| `script.yaml` | 89 キュー（床＋`pitch`） |
| `sfx.yaml` / `voice_fx.yaml` | `drama-beta00` から写しただけ |
| `mix.yaml` | `assemble.py` が書く（92 ステム） |
| `measure_pitch.py` | 床と 2 版を測り `probe.tsv` を書く |
| `probe.tsv` | 178 行＝89 キュー×2 版 |

音（`assets/drama-beta00-pitch/` の WAV）は追わない。同じ台詞・同じ seed で作り直せる。

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/experiments/scene/drama-beta00-pitch
PYTHONPATH=. $PY projects/longform/assemble.py --dir projects/longform/experiments/scene/drama-beta00-pitch
PYTHONPATH=. $PY projects/longform/experiments/scene/drama-beta00-pitch/measure_pitch.py
```
