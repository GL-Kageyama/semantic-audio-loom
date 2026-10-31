# longform-explainer — 解説「音は、なぜ感情を動かすのか」

5 分 11 秒の解説音。語り手ひとりと、実例の 4 本だけ真白が喋る。
**声・効果音・下地を別々に作って 1 本に組む**長尺の実例。

`explainer.mp3`（44.1kHz stereo / 192 kbps）が完成音。WAV は
`projects/longform/assets/explainer/renders/` に出る（約 5,500 万バイトなので追わない）。

## 中身

| 節 | 内容 |
| --- | --- |
| 導入 | 音は感情の説明ではない、という題の提示 |
| 一章 音量 | 大きさが意味を変える |
| 二章 間 | 間（無音そのものを 5 秒聴かせる実演つき） |
| 三章 音色 | 同じ高さ・大きさで質だけを変える |
| 実例（真白） | 「明日、また来るね。」を 3 通りで |
| 言葉にならない感情 | 喜怒哀楽の外（照れ・諦め・虚勢など） |
| 実例二（扉） | 静かに閉める／叩きつける／鳴らさない |
| まとめ | 音は感情の置き場所 |

章の鐘は 8 か所（`chapters.yaml` の cue）。

## 門の実測（`projects/longform/check_render.py`・`check_duck.py`）

| 項目 | 値 |
| --- | --- |
| 尺 | 311.2 秒（5.19 分） |
| ピーク / クリップ | −0.4 dBFS / 0 |
| 配布 mp3 | −18.16 LUFS / **−1.14 dBTP**（`deliver.py`・−0.45 dB の直線ゲイン） |
| 無音率 | 37.7%（1 秒以上の穴 27。最長 5.14 秒は q01→q02 の実演） |
| 効果音 10 本 | 鳴る直前の床から **+24.5〜+49.2 dB**（鐘 8・扉 2） |
| ducking | 中央値 **−11.7 dB**（上限 14 dB）。声の間の下地は −49.3 dBFS |

## 置いてあるファイル

| ファイル | 中身 |
| --- | --- |
| `explainer.mp3` | 完成音 |
| `script.yaml` | 48 キュー。台詞・感情・強度・声量・速さ・間 |
| `chapters.yaml` | 章の頭の cue 名（その 1.6 秒手前に鐘） |
| `sfx.yaml` | 扉 2 本の置き場所（cue 名＋手前の秒数）と利得 |
| `bed_mute.yaml` | 下地を止める間（`gap_after: q01`） |
| `mix.yaml` | 組み上げの記録（全 59 ステムの開始時刻と利得・ducking の設定） |

`mix.yaml` の `file:` は `projects/longform/assets/explainer/` を指す。生成物は追わないので、
名前だけが手元に残る。

## 聴きどころ

真白が同じ一行「明日、また来るね。」を、素と三通りで演じる場面がある。
**2:41.2（素 m01）・2:49.4（励まし m02）・3:00.1（別れ m03）・3:14.0（照れ隠し m04）。**

- 測った f0 は 326.0 / 355.5 / 347.3 / 355.5 Hz。抑揚は 8.0 / 9.6 / 8.2 / 9.4 半音。
- ⚠️ **3 つめ（照れ隠し）は、2 つめ（励まし）とほとんど同じ音**（包絡 0.11 dB・
  MFCC 5.4）。seed を替えると 0.85〜1.06 dB 動くので、方向の差はその内側に入る。
  同じ seed 1 では、方向を振っても声質が動く幅が小さい
  （[projects/longform/explainer-joy/](../../projects/longform/explainer-joy/)）。

## 作り方

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/explainer
./projects/longform/explainer/build_sound.sh          # 鐘・扉・下地（1 本 3〜13 分）
PYTHONPATH=. $PY projects/longform/assemble.py --dir projects/longform/explainer
```

詳しい手順は [../../projects/longform/README.md](../../projects/longform/README.md)。
