# longform-drama-pitch — 床の芝居に、`pitch` を人物へ振った版

「午前二時の電話」89 キューの**全部**に `pitch` を書き込んだ版。真白は `very_low`、
ニジは `high`、ほかは [longform-drama-beta00](../longform-drama-beta00/) と同じ
（`beta` 0.0・台詞・seed・間・効果音・帯域）。

8 行の聞き比べ（[longform-floor-two-speakers](../longform-floor-two-speakers/)）では
12 組すべてでニジが上になった。**それが作品 89 本でも成り立つか**を測るための版。

`drama-beta00-pitch.mp3`（44.1kHz stereo / 192 kbps）が完成音。4 分 51 秒。

## 何が分かったか

**上下は、作品の段でも開く。ただし代償が二つ出る。**

| 項目 | 床（beta 0.0） | 床＋pitch |
| --- | --- | --- |
| 尺 | 339.1 秒（5.65 分）→ 門 **合格** | **291.0 秒（4.85 分）→ 門 未達** |
| 生の声の合計（切る前） | 真白 134.1 / ニジ 137.5 秒 | **真白 89.0** / ニジ 139.2 秒 |
| f0 の中央値 | 真白 311.2 / ニジ 316.7 Hz | 真白 295.5 / ニジ 318.5 Hz |
| 感情の偏りを除いた二人の差（真白 − ニジ） | +0.1 Hz | **−13.4 Hz** |
| 感情 8 種の平均 f0 の幅 | 79.1 Hz | 69.5 Hz |
| 抑揚（8 感情の平均・半音） | 7.40 | **6.20**（真白 7.08 → 4.93 / ニジ 7.66 → 7.45） |
| 間（全キュー平均） | 0.136 | 0.110 |
| ニジが隣の真白より上のキュー | 21/42 | **31/42** |

- **高さの差は開く。** 感情の偏りを除くと、床は +0.1 Hz（＝差なし）だったのが
  **−13.4 Hz**（真白が下）になる。既定の `beta` 0.7 版の −8.5 Hz より広い。
  1 行ずつ隣と比べても、ニジが上になるのは 21/42 → **31/42**。
- **ただし `very_low` は高さだけを動かさない。** 真白の声は 134.1 → **89.0 秒**
  （−33.6%）。同じ台詞・同じ seed で、間が落ち、話す速さが上がり、抑揚が
  7.08 → **4.93 半音**に潰れる。ニジ（`high`）は 137.5 → 139.2 秒でほぼ動かない。
  語は DSP のノブではなくプロンプトの一文（`with a very low pitch`）なので、
  モデルはその一文ごと演技を組み直す。
- **その結果、尺の門を割る。** 48.1 秒縮んで 291.0 秒。5 分の門に 9 秒届かない。
  この版は配布用ではなく、**「高さで二人を分けると何を払うか」を見る版**。
- **縮むのは、長い（静かな・遅い）テイクから。** 真白の 1 キューあたりの短縮は、
  囁き −2.30 秒（3 本）・quiet −1.34（14 本）・normal −0.46（28 本）、
  速さでは very_slow −1.69（4 本）・slow −1.35（19 本）・natural −0.28（14 本）。
  **尺を使っている台詞ほど削られる。** ニジの側は変わらない（比の中央値 1.01）。

## 測り方

- f0 は `semantic_audio_loom/skills/act_probe.py` の `f0_median_hz`（有声区間の中央値）。
- 二人の差は、キューごとの f0 から**感情の平均を引いた残差**を人物ごとに平均し、
  真白 − ニジ を取った（同じ式で床は +0.1・`beta` 0.3 は −2.0・0.7 は −8.5 Hz になり、
  公表済みの値と一致する）。
- 「隣の真白より上」は、ニジのキューと、その前後で真白のキュー（±1）の平均 f0 を比べた数。
- 尺・無音・効果音は `projects/longform/check_render.py`、沈みは `check_duck.py`。

## 門（`projects/longform/check_render.py`）

| 項目 | 値 |
| --- | --- |
| 尺 | 291.0 秒（4.85 分）→ **未達**（門 5.0 分） |
| ピーク / クリップ | −0.4 dBFS / 0 |
| 無音率 | 34.1%（1 秒以上の穴 8 個・最長 1.34 秒） |
| 呼び出し音 | −58.5 → **+40.1 dB** |
| 切断音 | −48.4 → **+22.2 dB** |
| ducking（`check_duck.py`） | 中央値 **−11.6 dB**（指定の上限 14.0 dB） |

## 限界

- **人が聴いて確かめた版ではない。** 自動の門と測定だけを通した。
- 89 キューは 1 seed ずつ。**seed を振った再現は取っていない。**
- 「ニジが上」は f0 の中央値の比較で、**声の高さの知覚そのものは測っていない**。
- この版の包絡・MFCC は読んでいない（`pitch` をまたぐと倍音の間隔が動くため）。

## 置いてあるファイル

| ファイル | 中身 |
| --- | --- |
| `drama-beta00-pitch.mp3` | 完成音 |
| `script.yaml` | 89 キュー。床の各キューに `pitch: very_low`（真白 47）/ `pitch: high`（ニジ 42） |
| `sfx.yaml` / `voice_fx.yaml` | 元と同じ |
| `mix.yaml` | 組み上げの記録（92 ステム） |

## 作り方

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/drama-beta00-pitch
PYTHONPATH=. $PY projects/longform/assemble.py --dir projects/longform/drama-beta00-pitch
PYTHONPATH=. $PY projects/longform/check_render.py \
  projects/longform/assets/drama-beta00-pitch/renders/drama-beta00-pitch.wav \
  --mix projects/longform/drama-beta00-pitch/mix.yaml
```

下地と効果音は `projects/longform/assets/drama-beta00/` から写した。
