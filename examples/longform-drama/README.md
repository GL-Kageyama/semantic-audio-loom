# longform-drama — 二人芝居「午前二時の電話」

5 分 10 秒。真白とニジの電話。**同じモデルから出た二人の声をどう分けるか**が
この作品の主題でもある。`drama.mp3`（44.1kHz stereo / 192 kbps）が完成音。

## 筋

午前二時、三日つながらなかった電話が、今夜だけつながる。ニジはどこにいるのか
言わない。怒り、軽口、諦め、笑い、そして切断。最後は真白の独白。

| 節 | 内容 |
| --- | --- |
| 呼び出し | 呼び出し音のあと「……もしもし。」 |
| 軽口（照れ） | 怒りが小声になる癖をニジが指摘する |
| なんで今なのか | なぜ今夜なのか |
| どうでもいい話 | 笑いの底に諦めを沈める |
| 打ち明け | ニジが理由を言う |
| 怒り / 泣き笑い | 喜怒哀楽の外を、音量と間と音色に置く |
| 思い出 | 昔の話 |
| 切断 | 長い間のあと、切れる音 |
| 独白 | 真白ひとり |

## 二人の声の分け方

同じモデルから出た二人は、**seed の揺れのほうが人物差より大きい**
（3 台詞 × 2 人物 × seed 3＝18 本・beta 0.7 の有声フレーム距離：同一人物（seed 違い）
16.4、別人（同じ台詞・同じ seed）13.8）。声そのものでは聞き分けられない。

そこでニジだけ `voice_fx.yaml` で電話の帯域（320–3400 Hz・+3 dB）に通している。
組み上げ後の実測（声の帯域の比、`projects/longform/drama/mix.yaml` の声 89 本）：

| 人物 | 本数 | 低域 | 中域 | 高域 |
| --- | --- | --- | --- | --- |
| 真白 | 47 | −4.6 dB | −2.3 dB | −17.2 dB |
| ニジ | 42 | −9.9 dB | −0.6 dB | −26.5 dB |

低域が 5.3 dB、高域が 9.3 dB 低い。帯域は演技ではなく**配色**の層。

## 門の実測（`projects/longform/check_render.py`・`check_duck.py`）

| 項目 | 値 |
| --- | --- |
| 尺 | 310.6 秒（5.18 分） |
| ピーク / クリップ | −0.4 dBFS / 0 |
| 配布 mp3 | −16.95 LUFS / **−1.17 dBTP**（`deliver.py`・−0.45 dB の直線ゲイン） |
| 無音率 | 40.5%（1 秒以上の穴 11。最長 1.68 秒は末尾の余白） |
| 呼び出し音 | 鳴る直前の床 −58.6 dBFS → **+40.1 dB** |
| 切断音 | −47.5 dBFS → **+22.1 dB** |
| ducking | 中央値 **−11.2 dB**。声の間の環境音 −43.8 dBFS／声の上 −50.2 dBFS |
| 機械的な欠陥 | なし（重心 583 Hz・平坦度 0.0004＝ヒス無し） |

## 置いてあるファイル

| ファイル | 中身 |
| --- | --- |
| `drama.mp3` | 完成音 |
| `script.yaml` | 89 キュー（s01–s72・y01–y17）。台詞・感情・強度・声量・速さ・間 |
| `sfx.yaml` | 呼び出し音と切断音の置き場所 |
| `voice_fx.yaml` | ニジの帯域（電話） |
| `mix.yaml` | 組み上げの記録（92 ステムの開始時刻と利得・ducking の設定） |

## 作り方

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/drama
./projects/longform/drama/build_sound.sh
PYTHONPATH=. $PY projects/longform/assemble.py --dir projects/longform/drama
```

詳しい手順は [../../projects/longform/README.md](../../projects/longform/README.md)。
