# mashiro-night — サンプル生成

『午前二時に、あなたは誰の時間を生きていますか』（`soul-voice-teller/examples/gozen-niji`）の
主人公・**真白**（高校二年生）の声。参照音声なしの**経路B**で作った専用の元音声
（`references/mashiro.wav`）を timbre の実体にし、台詞「うん、行ってらっしゃい。」を生成した例。

| 入力 | 値 |
| --- | --- |
| キャラ | `mashiro`（`characters/mashiro.voice.yaml`・`adolescent` / `soft` / `slight` / `intimate`） |
| 元音声 | `references/mashiro.wav`（経路B `synthesize` で生成・登録） |
| 台詞 | うん、行ってらっしゃい。 |
| 演技 | sadness / restrained / quiet / slow（CLI フラグ指定） |
| subtext | 名指ししない別れ。二度と会えないと知りながら、泣く代わりに穏やかに送り出す。 |
| seed | 132070274 |

- `mashiro_itterasshai.wav` … 生成された音声（24kHz・mono）
- `mashiro_itterasshai.params.yaml` … 保存済み Performance Spec（再生成の入力）

## 再生成

```bash
# 保存済み Spec を再利用（LLM は呼ばない・Tsukasa が必要）
bin/regenerate.py examples/mashiro-night/mashiro_itterasshai.params.yaml --out-dir /tmp/regen

# ゼロから同じ指定で生成（経路A: timbre は references/mashiro.wav から）
bin/generate.py --character mashiro --project gozen-niji --scene ch12 \
    --line "うん、行ってらっしゃい。" \
    --emotion sadness --delivery restrained --volume quiet --speed slow \
    --subtext "名指ししない別れ。二度と会えないと知りながら、泣く代わりに穏やかに送り出す。" \
    --resolve rule --name mashiro_itterasshai --seed 132070274
```

> 元音声（参照音声）の作り直しは `bin/reference.py synthesize mashiro --character mashiro`。
> subtext を抑揚に変換する `--resolve llm` を使う場合は `SAL_RESOLVE_MODEL` を設定する
> （既定 `claude-sonnet-4-5` は DeepSeek ゲートウェイでは受け付けないため）。
