# gozen-niji-katari-scenes — 語りの代表シーン音声

『午前二時に、あなたは誰の時間を生きていますか』（`soul-voice-teller/examples/gozen-niji`）の
**三人称ナレーション（語り）**の声（`characters/gozen-niji-katari.voice.yaml`・
`references/gozen-niji-katari.wav`）で、design.md「語り」の文体をたどる 5 つの地の文パッセージを
生成したもの。

語りは物語の登場人物ではなく、地の文を担う声。**真白の肩越しの三人称**で、説明しない・
名指ししない・総括しない。真白の内面も、感情の総括でなく「観察・身体・行為」で示す。
persona の声（ソリッド・無駄をそぎ落とす・リズミカル・行間に意味）に照合し、短文（切断・疾走）
と長文（思考・反芻）の配分でリズムを作り、読点は並列を一息で流し、要の一打だけに刻む。
地の文（語り）は真白の逡巡を帯びる（「〜だった」「〜かもしれない」）。

声質は adult / neutral / chest で、真白（adolescent / soft / intimate）より成熟し、
ニジ（high / clear / head）より地に足が付いた、胸に響くナレーション。三者の使い分けが
そのまま**語り（地の文）・真白（独白）・ニジ（台詞）**の音のコントラストになる。

元になった地の文は各話の草稿から抽出した語りの実際のパッセージ。`――` は TTS に乗らないため
省き、間は `delivery`（controlled / restrained / gentle）と `speed`（natural / slow）で
表現している。

## シーン一覧（語りの文体）

| 話 | ファイル | 地の文（語り） | 感情 | delivery | subtext |
| --- | --- | --- | --- | --- | --- |
| 第1話 | `katari_ch01_opening.wav` | 夜の十一時。真白は、布団の中で、スマホをいじっていた。画面の光が、部屋の暗い天井に、ぼんやりと、薄い青を塗ってた。 | calm / subtle / quiet | controlled | 深夜の静けさ。真白の日常を、説明せず観察だけして示す。 |
| 第1話 | `katari_ch01_body.wav` | 親指の先だけが、熱を持ってた。今夜、何度、同じ指が、同じ場所を、撫でたか、分からなかった。 | calm / subtle / quiet | restrained | 無意識に撫で続ける指。行動だけが内面を語る。 |
| 第1話 | `katari_ch01_refrain.wav` | 既読を付けて、画面を閉じる。それが、一番、関係を壊さない。真白は、そう、自分に言い聞かせていた。 | calm / subtle / quiet | restrained | 関係を壊さないために返さない。自分に言い聞かせる言葉。 |
| 第1話 | `katari_ch01_clock.wav` | 眠ろうとして、目を閉じる。でも、目が覚める。夜中に、一度。時計を見る。午前2時。 | neutral / subtle / quiet | controlled | 眠れない夜の、時間の刻み。 |
| 第12話 | `katari_ch12_ending.wav` | 真白は、スマホを閉じた。朝の光が、窓から差してた。真白は、立ち上がって、カーテンを開けた。外は、晴れてた。 | calm / subtle / quiet | gentle | 名指ししない決着。スマホを閉じ、外へ踏み出す。解放は行為で示す。 |

- 各 `.wav` … 生成された音声（24kHz・mono）
- 各 `.params.yaml` … 保存済み Performance Spec（再生成の入力）

`speed` は語りのリズムを担う——短文の疾走（opening / clock）は `natural`、思考・反芻
（body / refrain）は `slow`、決着の解放（ending）は `natural` + `gentle`。

`katari_ch01_refrain` は、Tsukasa の phonemize が「既読」を `きよみ` と誤読するため、
台詞にふりがな `漢字《かな》` を指定して「きどく」に直している。`《》` は読みにだけ使われ、
保存される台詞（`dialogue`）からは外れる（読みは `reading` として params に保存）。

キャラ名（固有名詞）も phonemize が誤読する（「真白」→「まっしろ」）。これは `characters/mashiro.voice.yaml`
の `name_reading: ましろ` により、台詞中の「真白」へ自動でふりがなが振られる（手書き《》は不要）。
opening / refrain / ending の 3 サンプルはこの自動ふりがなで「ましろ」と発音される。

## 再生成

```bash
# ゼロから（経路A: timbre は references/gozen-niji-katari.wav から）
bin/generate.py --character gozen-niji-katari --project gozen-niji --scene katari-03 \
    --line "既読《きどく》を付けて、画面を閉じる。それが、一番、関係を壊さない。真白は、そう、自分に言い聞かせていた。" \
    --emotion calm --intensity subtle --volume quiet --speed slow --delivery restrained \
    --subtext "関係を壊さないために返さない。自分に言い聞かせる言葉。" \
    --resolve rule --name katari_ch01_refrain --seed 202

# 保存済み Spec を再利用（LLM は呼ばない・Tsukasa が必要）
bin/regenerate.py examples/gozen-niji-katari-scenes/katari_ch01_refrain.params.yaml --out-dir /tmp/regen
```

> 台詞の裏の意味を抑揚に変換する `--resolve llm` を使う場合は `SAL_RESOLVE_MODEL` を設定する
> （既定 `claude-sonnet-4-5` は DeepSeek ゲートウェイでは受け付けないため）。本サンプルは
> 決定的写像（`--resolve rule`・`intonation: neutral`）で生成している。
>
> 元音声（参照音声）の作り直しは `bin/reference.py synthesize gozen-niji-katari --character gozen-niji-katari`。
