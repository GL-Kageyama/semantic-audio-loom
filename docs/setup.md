# セットアップ — クローンから動くまで

リポジトリ内で完結するもの（コード・キャラ・演技・参照音声）と、外部に置くもの
（モデル・依存）を分ける。

## 1. Python 依存

```bash
pip install -r requirements.txt
```

- コア（キャラ/演技/参照音声の管理、スキーマ検証、Resolve、蒸留）だけでよければ
  `numpy / PyYAML / jsonschema` のみで動く。
- 生成実行時（Tsukasa）は `torch / cutlet / librosa / soundfile / scipy` が要る。
  これらは生成専用で重いため、コアとは別に Tsukasa 実行環境へ入れる。

## 2. Tsukasa_Speech チェックアウト（生成実行時のみ）

音声合成は Tsukasa が担う。モデル（~5GB）は外部に置き、環境変数で指す：

```bash
export SAL_TSUKASA_DIR=/path/to/tsukasa
```

生成しなければ不要。キャラ/演技/参照音声の管理や蒸留は Tsukasa なしで動く。

## 3. Resolve の LLM（--resolve llm 時・既定）

```bash
export ANTHROPIC_AUTH_TOKEN=...      # または ANTHROPIC_API_KEY=...
export ANTHROPIC_BASE_URL=...        # ゲートウェイ。モデルは SAL_RESOLVE_MODEL で変更可
```

`--resolve rule`（決定的写像）なら LLM なしで Spec まで生成できる（音声合成は Tsukasa が要る）。

## 同梱済みの資材

キャラ（`characters/`）・演技（`performances/`）・参照音声（`references/`）は同梱済み。
クローンすれば `bin/character.py list` や `bin/reference.py list` がそのまま動く。

## 環境変数

| 変数 | 意味 |
| --- | --- |
| `SAL_TSUKASA_DIR` | Tsukasa チェックアウト（生成実行時に必要） |
| `SAL_REFERENCE_LIB` | 参照音声ライブラリ（既定は repo 直下 `references/`） |
| `SAL_CHARACTERS_DIR` | キャラ資材（既定は repo 直下 `characters/`） |
| `SAL_PERFORMANCES_DIR` | 演技資材（既定は repo 直下 `performances/`） |
| `SAL_RESOLVE_MODEL` | Resolve のモデル（既定 claude-sonnet-4-5） |
