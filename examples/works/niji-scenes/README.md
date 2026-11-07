# niji-scenes — ニジの代表シーン音声

『午前二時に、あなたは誰の時間を生きていますか』（`soul-voice-teller/examples/gozen-niji`）の
「午前二時の幽霊」**ニジ**の声（`characters/niji.voice.yaml`・`references/niji.wav`）で、
彼の感情の弧をたどる 5 つの代表シーンを生成したもの。

ニジは真白が画面越しの虹色の残像に名付けた存在。正体は「真白が誰かに預けた時間＝
他者の感情の結晶」で、**真白と同じ顔、でも一歩手前に少し幼く**、正直すぎるほど正直で
無邪気、かつ「返せたら帰れる」と最初から知っている達観を持つ。声は「おまえ」呼び・
句点で切るリズム・空気を含ませ・真白より一拍ゆっくり（design.md 2-13）。

元になった台詞は各話の草稿から抽出したニジの実際の発話。`――` は TTS に乗らないため
省き、間は `delivery: gentle` と `pace: slow` で表現している。

## シーン一覧（感情の弧）

| 話 | ファイル | 台詞 | 感情 | delivery | subtext |
| --- | --- | --- | --- | --- | --- |
| 第3話 | `niji_ch03.wav` | びっくりした？ ごめんね。でも、おまえ、昨日、起きてたじゃん。 | joy / moderate / normal | cheerful | 初めて自分を見つけてくれた人間への、無邪気な親しみと正直さ。 |
| 第4話 | `niji_ch04.wav` | だって、預けたんだもの。減らしても、消えない。返すまで、ずっと、残るんだよ | calm / moderate / quiet | gentle | 逃げても無駄だと、達観して諭す。返すまで消えない。 |
| 第5話 | `niji_ch05.wav` | 次は、おまえが届けなよ | calm / subtle / quiet | gentle | 真白自身に、言葉を届けさせようとする静かな背押し。 |
| 第8話 | `niji_ch08.wav` | 返してくれたら、わたしは、帰れる | sadness / subtle / quiet | gentle | 初めて自分を主語にした言葉。帰れる、と知っている寂しさ。 |
| 第12話 | `niji_ch12.wav` | 返してくれて、ありがとう | sadness / subtle / quiet | gentle | 返してくれたことへの感謝と、穏やかな別れ。 |

- 各 `.wav` … 生成された音声（24kHz・mono）
- 各 `.params.yaml` … 保存済み Performance Spec（再生成の入力）

## 再生成

```bash
# ゼロから（経路A: timbre は references/niji.wav から）
bin/generate.py --character niji --project gozen-niji --scene niji-03 \
    --line "びっくりした？ ごめんね。でも、おまえ、昨日、起きてたじゃん。" \
    --emotion joy --intensity moderate --volume normal --speed natural \
    --delivery cheerful --subtext "初めて自分を見つけてくれた人間への、無邪気な親しみと正直さ。" \
    --resolve rule --name niji_ch03 --seed 100

# 保存済み Spec を再利用（LLM は呼ばない・Tsukasa が必要）
bin/regenerate.py examples/niji-scenes/niji_ch03.params.yaml --out-dir /tmp/regen
```

> 台詞の裏の意味を抑揚に変換する `--resolve llm` を使う場合は `SAL_RESOLVE_MODEL` を設定する
> （既定 `claude-sonnet-4-5` は DeepSeek ゲートウェイでは受け付けないため）。本サンプルは
> 決定的写像（`--resolve rule`・`intonation: neutral`）で生成している。
>
> 元音声（参照音声）の作り直しは `bin/reference.py synthesize niji --character niji`。
