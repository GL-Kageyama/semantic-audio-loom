# longform-drama-beta03 — 「午前二時の電話」を beta 0.3 で組み直した版

5 分 32 秒。台詞・seed・間・効果音・ducking は [longform-drama](../longform-drama/) と同じで、
**声の混ぜ方（beta）だけ 0.7 → 0.3** にした。演技が乗る代わりに声質が参照音声から
離れる——その代償を、作品の単位で聞き比べるための版。

`drama-beta03.mp3`（44.1kHz stereo / 192 kbps）が完成音。

## 何が変わったか（実測）

| 項目 | beta 0.7（`longform-drama`） | beta 0.3（この版） |
| --- | --- | --- |
| 尺 | 310.5 秒 | **332.2 秒**（+21.7 秒・+7.0%） |
| 声の実時間（頭尾の無音を切った後） | 217.3 秒 | **239.0 秒** |
| 生の声の合計（切る前） | 271.3 秒 | 271.1 秒 |
| 参照声（`references/mashiro.wav`）との MFCC 距離（11 本の中央値） | 34.3 | **46.5** |
| ピーク / クリップ | −0.4 dBFS / 0 | −0.4 dBFS / 0 |
| ducking 中央値 | −11.2 dB | −11.3 dB |
| 呼び出し音 / 切断音の立ち上がり | +40.1 / +22.1 dB | +40.0 / +20.0 dB |

- **生の声は同じ長さなのに、切った後の声は 21.7 秒長い。** beta 0.3 の声は頭尾の
  無音が少なく、語りが長く続く。作品の尺が伸びたのはこれ（間を足したのではない）。
- 声質は参照から離れる（34.3 → 46.5）。演技の代償は作品単位でも残る。

### 代表 12 キューの変化（秒・f0 中央値）

| cue | 感情 | 秒 0.7 → 0.3 | f0 0.7 → 0.3 Hz |
| --- | --- | --- | --- |
| s01 | anxiety | 2.27 → 2.62 | 292.1 → 292.1 |
| s02 | calm | 2.22 → 2.57 | 300.6 → 278.9 |
| s04 | joy | 4.05 → 3.40 | 335.5 → 335.5 |
| s07 | sadness | 3.87 → 3.87 | 277.3 → 277.3 |
| s09 | anger | 3.30 → 2.87 | 267.8 → 255.7 |
| s13 | sadness | 2.22 → 2.70 | 357.5 → 326.0 |
| s14 | joy | 5.40 → 4.87 | 341.4 → 351.4 |
| s16 | joy | 3.70 → 3.20 | 353.4 → 343.4 |
| s19 | sadness | 4.20 → 4.20 | 329.7 → 316.7 |
| s24 | joy | 3.55 → 3.32 | 336.5 → 345.3 |
| s31 | anger | 4.10 → 3.77 | 304.1 → 331.7 |
| y05 | joy | 2.00 → 2.05 | 318.5 → 305.9 |

**cue ごとの差は小さい。** beta 0.3 で大きく分かれるのは、感情の覚醒
（neutral 対 anger・joy）を同じ口調で振ったとき（[REPORT §beta](../../projects/longform/REPORT.md)）。
この脚本はもともと delivery・速さ・声量で演技を置いているので、beta を下げても
同じ向きに二重で動くだけになる。

## 門（`projects/longform/check_render.py`）

| 項目 | 値 |
| --- | --- |
| 尺 | 332.2 秒（5.54 分）→ 合格 |
| ピーク / クリップ | −0.4 dBFS / 0 |
| 無音率 | 35.7%（1 秒以上の穴 9。最長 1.08 秒） |
| 呼び出し音 | 鳴る直前 −58.3 dBFS → **+40.0 dB** |
| 切断音 | −45.4 dBFS → **+20.0 dB** |
| ducking（`check_duck.py`） | 中央値 **−11.3 dB**（指定の上限 14.0 dB） |

## 限界

- **人が聴いて確かめた版ではない。** 自動の門（尺・クリップ・無音・効果音の立ち上がり・
  ducking）だけを通した。
- 声は参照音声から離れる（上の MFCC 距離）。人の耳で「同じ人が喋っている」と
  聞こえるかは未確認。

## 置いてあるファイル

| ファイル | 中身 |
| --- | --- |
| `drama-beta03.mp3` | 完成音 |
| `script.yaml` | 89 キュー。すべて `beta: 0.3`（元の `script.yaml` に 1 行ずつ足しただけ） |
| `sfx.yaml` / `voice_fx.yaml` | 元と同じ |
| `mix.yaml` | 組み上げの記録（92 ステム） |

## 作り方

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/drama-beta03
PYTHONPATH=. $PY projects/longform/assemble.py --dir projects/longform/drama-beta03
```

下地（`bgm/underlay.wav`）と効果音は `projects/longform/assets/drama/` から写した。
