# mashiro-scenes — 真白の代表シーン音声

『午前二時に、あなたは誰の時間を生きていますか』（`soul-voice-teller/examples/gozen-niji`）の
主人公・**真白**の声（`characters/mashiro.voice.yaml`・`references/mashiro.wav`）で、
彼女の感情の弧をたどる 5 つの代表シーンを生成したもの。

元になった台詞は各話の草稿（`gozen-niji/草稿/`）から抽出した真白の実際の発話
（`「」` で囲まれた台詞。内言 `――` やニジの台詞 `＞` は除外）。先頭の `……` は
TTS に乗らないため省き、間は `delivery`（hesitant/gentle）と `pace: slow` で表現している。

## シーン一覧（感情の弧）

| 話 | ファイル | 台詞 | 感情 | delivery | subtext |
| --- | --- | --- | --- | --- | --- |
| 第2話 | `mashiro_ch02.wav` | 誰、あなた | fear / subtle / whisper | hesitant | 得体の知れないものへの警戒。本当にそこにいるのか、確かめられない。 |
| 第3話 | `mashiro_ch03.wav` | ニジ | calm / subtle / quiet | intimate | 名前のない存在に、私のものとして名前を与える瞬間。 |
| 第5話 | `mashiro_ch05.wav` | 嬉しい、って気持ちが、こっちまで届いてくる | calm / moderate / quiet | subtle | 届くはずのない他者の嬉しさに、初めて触れた戸惑いと驚き。 |
| 第11話 | `mashiro_ch11.wav` | 私、あなたに、時間を預けてました | anxiety / moderate / quiet | hesitant | ずっと言えなかったこと。知らずに、あなたの時間を預かっていた。 |
| 第12話 | `mashiro_ch12.wav` | うん。また、明日 | sadness / subtle / quiet | gentle | 二度と会えないと知りながら、それでも明日を約束する。 |

（第12話の「うん、行ってらっしゃい。」は `examples/mashiro-night/` に別途収録）

- 各 `.wav` … 生成された音声（24kHz・mono）
- 各 `.params.yaml` … 保存済み Performance Spec（再生成の入力）

## 再生成

```bash
# ゼロから（経路A: timbre は references/mashiro.wav から）
bin/generate.py --character mashiro --project gozen-niji --scene ch02 \
    --line "誰、あなた" --emotion fear --intensity subtle --volume whisper --speed slow \
    --delivery hesitant --subtext "得体の知れないものへの警戒。…" \
    --resolve rule --name mashiro_ch02 --seed 42

# 保存済み Spec を再利用（LLM は呼ばない・Tsukasa が必要）
bin/regenerate.py examples/mashiro-scenes/mashiro_ch02.params.yaml --out-dir /tmp/regen
```

> 台詞の裏の意味を抑揚に変換する `--resolve llm` を使う場合は `SAL_RESOLVE_MODEL` を設定する
> （既定 `claude-sonnet-4-5` は DeepSeek ゲートウェイでは受け付けないため）。本サンプルは
> 決定的写像（`--resolve rule`・`intonation: neutral`）で生成している。
