# Distill — 大量のインプットを資材へ折りたたむ（M4）

## 何をするか

物語・脚本・人物描写といった「大量のインプット」から、再利用資材を自動生成する。
手で埋める `character.py init` / `performance.py init` の代わりに、テキストを蒸留して
`characters/<name>.voice.yaml` と `performances/<name>.direction.yaml` を作る。

```
大量インプット（物語・脚本・人物描写）
        → ①理解 → ②選択 → ③翻訳（schema の enum へ）
        → characters/ + performances/（＋ --synthesize で references/）
```

distill-essence-engine の「蒸留」を音声資材向けに翻案したもの。違いは出力先だけで、
音声蒸留では ③翻訳 の出力が **schema の enum 制約を持つ構造化 YAML** に落ちる。

## 二モード

| モード | コマンド | 入力 → 出力 |
| --- | --- | --- |
| batch（一括蒸留） | `bin/distill.py batch` | 物語1つ → 主要キャラ複数 × 代表シーン複数 |
| single（単発抽出） | `bin/distill.py character` / `performance` | 1入力 → キャラ1体 / 演技1つ |

## 蒸留の三手順

1. **①理解** — 登場人物の声質（年齢・性別・ピッチ・質感・息・共鳴）と、シーンの感情・状況・台詞・subtext を掴む。
2. **②選択** — 全員・全シーンではなく主要キャラ（目安 5 人以内）・代表シーン（目安 6 つ以内）を選ぶ。無限を有限に折りたたむ。
3. **③翻訳** — 描写を schema の enum（`pitch: very_low〜very_high` 等）へ必ず収めて翻訳する。enum 外は出さない。

## 崩れた出力は再生成

Resolve と同じ方針。LLM が enum 外の値を出したり、必須フィールド（`age`/`pitch`/`texture`/`breathiness` や `emotion`）を欠いたりしたら、
手で直さず**再生成**する（`_distill` が最大 3 回再試行し、最後まで崩れれば例外で止まる）。

## schema 制約

- キャラ: `voice_profile.schema.json`（required: `age` / `pitch` / `texture` / `breathiness`）
- 演技: `performance_asset.schema.json`（required: `emotion`）

書き出しは `validate.validate_voice_profile` / `validate_performance_asset` を通したものだけ。

## 元音声の実体化（--synthesize）

蒸留した `voice`（声質）から、`--synthesize` で参照音声も経路B（Tsukasa・参照不要）で生成し、
`references/` に登録、`.voice.yaml` の `reference_audio` にそのキーを指す。経路B は女性バイアスが強い
（男性の深い声・老人は弱い）ので、確実な声は `bin/reference.py add`（著作権フリー音源）が向く。
