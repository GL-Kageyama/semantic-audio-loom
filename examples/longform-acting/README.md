# 聞き比べ — 「明日、また来るね。」

同じ一言を、声の混ぜ方（`beta`）だけ変えて並べた 74 秒の見本。語り手が札を読み、
真白（`characters/mashiro.voice.yaml`）が毎回同じ台詞を言う。

- 前半（beta 0.7＝既定）… 無表情・喜び・怒り・悲しみ・喜び（強）
- 後半（beta 0.3）… 同じ 5 本

`beta` は「プロンプトから作った演技の成分をどれだけ混ぜるか」のノブ。
下げるほど演技は出るが、参照音声の声質から離れる。

## 並び

| 秒 | 中身 |
| --- | --- |
| 1.4 | 導入（語り手） |
| 7.3 | 「まず、既定の混ぜ方。」 |
| 9.9 / 12.3 | 無表情 → 台詞（beta 0.7） |
| 14.9 / 16.9 | 喜び → 台詞 |
| 19.5 / 21.2 | 怒り → 台詞 |
| 23.9 / 26.1 | 悲しみ → 台詞 |
| 29.3 / 31.9 | 喜び（強）→ 台詞 |
| 35.8 | 「次は、演技の混ぜ方を強めます。」 |
| 39.1 / 41.4 | 無表情 → 台詞（beta 0.3） |
| 43.7 / 45.7 | 喜び → 台詞 |
| 48.4 / 50.0 | 怒り → 台詞 |
| 52.8 / 55.0 | 悲しみ → 台詞 |
| 58.2 / 60.8 | 喜び（強）→ 台詞 |
| 65.0 | 結び（語り手） |

## 実測（f0 中央値・この 1 本ずつ）

| 台詞 | beta 0.7 | beta 0.3 |
| --- | --- | --- |
| 無表情 | 326.0 Hz | 280.5 Hz |
| 喜び | 351.4 | 339.4 |
| 怒り | 347.3 | 333.6 |
| 悲しみ | 331.7 | 298.9 |
| 喜び（強） | 360.6 | 359.6 |

beta 0.3 では無表情（280）と悲しみ（299）が低く、怒り（334）・喜び（339）・
喜び強（360）が高い。**分かれるのは覚醒の段**で、喜びと怒りは近い。
beta 0.7 では 5 本とも 326〜361 Hz に集まり、差が小さい。

## 作る

```zsh
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/acting-demo
PYTHONPATH=. $PY projects/longform/assemble.py --dir projects/longform/acting-demo
ffmpeg -i projects/longform/assets/acting-demo/renders/acting-demo.wav -b:a 192k examples/longform-acting/acting-demo.mp3
```

`script.yaml` の `beta:` は `build_voice.py` が読む（Scene 仕様の欄ではない）。
台詞はすべて seed 1。5 seed の中央値と 5/5 判定は
[projects/longform/REPORT.md](../../projects/longform/REPORT.md) を見る。

## 限界

- **意味の写像ではない。** 感情を強めると f0 は上がる。悲しみの subtle → strong は
  285 → 334 Hz（beta 0.3・5 seed の中央値）で、悲しみでも**上がる**。
  「悲しければ低い声」にはならない。
- 演技は**声の状態**（高さ・起伏・間・速さ）を変えて出ている。声そのもの（LPC 包絡）は
  beta 0.7 で 2.69 dB・0.0 で 1.80 dB と、下げるほど参照に近づく。
- 有声の高さ・長さ・強さは測れるが、「泣けるか」は測れない。
