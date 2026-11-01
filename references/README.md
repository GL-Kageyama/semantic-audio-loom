# 参照音声ライブラリ（references/）

経路A（`compute_style_through_clip`）で声の timbre を複製する元となる参照音声。
老若男女 10 名。各 WAV は話者の複数発話を連結した ~7〜9 秒クリップ（24kHz mono PCM16）。

`.voice.yaml` の `reference_audio` にここに並ぶ話者キー（例: `female_young_p308`）を書くと、
その声から timbre を固定して台詞を生成できる。

## 出典・ライセンス

| 出典 | ライセンス | 話者 |
| --- | --- | --- |
| **CSTR VCTK Corpus 0.92**（`sanchit-gandhi/vctk` 経由） | **CC BY 4.0** — Veaux, Yamagishi, MacDonald (2017) | 若〜壮年 8 名（英語） |
| **Common Voice**（`aviroes/mascir_elderly_voice` 経由・locale=fr） | **CC0**（話者は匿名 client_id） | 老人 2 名（フランス語） |

> 再配布する場合、VCTK 分は CC BY 4.0 の帰属表示が必須。Common Voice 分は CC0（帰属不要）。
> 各ファイルの詳細（話者 ID・年齢・出典ファイル）は `manifest.json` を参照。

## 収録話者（10 名）

| ファイル | 性別 | 年齢 |
| --- | --- | --- |
| `female_young_p308` | F | 18 |
| `female_adult_p225` | F | 23 |
| `female_adult_p280` | F | 25 |
| `female_mature_p294` | F | 33 |
| `male_young_p334` | M | 18 |
| `male_adult_p256` | M | 24 |
| `male_adult_p347` | M | 26 |
| `male_mature_p227` | M | 38 |
| `elderly_male` | M | 70代 |
| `elderly_female` | F | 60代 |

`seeds.json` は話者別の決定論 seed（境界話者の複製 f0 を性別域に固定するために検証で確定した値）。

## 生成した参照（映像生成から）

欲しい声が上の10名に無いときは、**動画生成に喋らせて、その音声を参照にする**。
仕様は `semantic-visual-loom/projects/explainer-voice-samples/`（声以外を揃えた4本）。

| ファイル | 声 | 出典 |
| --- | --- | --- |
| `gen_female_light` | 若い成人女性・明るく軽い | WAN 3.0 / `vs-01` |
| `gen_female_steady` | 成人女性・落ち着き・中高域 | WAN 3.0 / `vs-02` |
| `gen_machine_clear` | 機体・澄んだ高い声 | WAN 3.0 / `vs-03` |
| `gen_machine_bright` | 機体・さらに高く軽い | WAN 3.0 / `vs-04` |

**取り出す手順**：動画から `-vn -ac 1 -ar 24000 -c:a pcm_s16le`、頭尾の無音を切る。
10秒の素材は、切ると ~9秒になる（このライブラリの他の参照と同じ長さ）。
⚠️ **声の比較に使うときは、4本とも同じ台詞・同じ尺・同じ構図で録る**——条件が違えば音色の比較にならない。

## 拡充

足りない声は `bin/reference.py` で拡充する：

- `synthesize <key> --character <name>` … ローカル生成（Tsukasa 経路B・参照不要）
- `add <wav> <key> --license … --source …` … 著作権フリー音源の登録

登録時は必ず出典・ライセンスを `manifest.json` に記録する（配布時の帰属表示のため）。
