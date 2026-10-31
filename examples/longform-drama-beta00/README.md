# longform-drama-beta00 — 「午前二時の電話」を床（beta 0.0）で組み直した版

5 分 39 秒。台詞・seed・間・効果音・ducking は [longform-drama](../longform-drama/) と
同じで、**声の混ぜ方（beta）だけ 0.7 → 0.0** にした。beta 0.0 は prosody が全部
Kotodama プロンプト由来になる段（演技は最大、声は参照から最も遠い）。

三つ並べると、演技と代償の段が耳で辿れる：
[0.7](../longform-drama/)（既定）→ [0.3](../longform-drama-beta03/) → この 0.0。

`drama-beta00.mp3`（44.1kHz stereo / 192 kbps）が完成音。

## 三つの版（実測）

| 項目 | beta 0.7 | beta 0.3 | beta 0.0 |
| --- | --- | --- | --- |
| 尺 | 310.5 秒 | 332.2 秒 | **339.1 秒** |
| 生の声の合計（切る前） | 271.3 秒 | 271.1 秒 | 271.6 秒 |
| 切った後の声 | 217.3 秒 | 239.0 秒 | **245.9 秒** |
| 参照声（`references/mashiro.wav`）との MFCC 距離（真白 72 本の中央値） | 24.6 | 46.2 | **65.5** |
| ピーク / クリップ | −0.4 dBFS / 0 | −0.4 dBFS / 0 | −0.4 dBFS / 0 |
| 無音率 | 40.5% | 35.7% | 31.5% |
| ducking 中央値 | −11.2 dB | −11.3 dB | −11.7 dB |
| 呼び出し音 / 切断音の立ち上がり | +40.1 / +22.1 dB | +40.0 / +20.0 dB | +40.0 / +24.8 dB |

- **生の声は三つとも同じ長さ**（271 秒台）。尺が伸びるのは、切った後に残る声が
  長くなるから（head/tail の無音が減る）。0.7 → 0.0 で尺は +28.6 秒（+9.2%）。
- **声質は段ごとに離れる**（24.6 → 46.2 → 65.5）。0.3 → 0.0 の差（+19.3）は
  0.7 → 0.3 の差（+21.6）と同じくらい。**床まで下ろしても、代償の伸びは止まらない。**

## 門（`projects/longform/check_render.py`）

| 項目 | 値 |
| --- | --- |
| 尺 | 339.1 秒（5.65 分）→ 合格 |
| ピーク / クリップ | −0.4 dBFS / 0 |
| 無音率 | 31.5%（1 秒以上の穴 2。最長 1.04 秒） |
| 呼び出し音 | −58.1 → **+40.0 dB** |
| 切断音 | −50.6 → **+24.8 dB** |
| ducking（`check_duck.py`） | 中央値 **−11.7 dB**（指定の上限 14.0 dB） |

## 限界

- **人が聴いて確かめた版ではない。** 自動の門だけを通した。
- 声は参照音声から大きく離れる（上の MFCC 距離 65.5）。「同じ人が喋っている」とは
  聞こえない可能性が高い。**演技の上限を見るための版**で、配布用ではない。

## 置いてあるファイル

| ファイル | 中身 |
| --- | --- |
| `drama-beta00.mp3` | 完成音 |
| `script.yaml` | 89 キュー。すべて `beta: 0.0`（beta 0.3 版の 1 行を置き換えただけ） |
| `sfx.yaml` / `voice_fx.yaml` | 元と同じ |
| `mix.yaml` | 組み上げの記録（92 ステム） |

## 作り方

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/drama-beta00
PYTHONPATH=. $PY projects/longform/assemble.py --dir projects/longform/drama-beta00
```

下地（`bgm/underlay.wav`）と効果音は `projects/longform/assets/drama-beta03/` から写した。
