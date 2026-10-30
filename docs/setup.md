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

## 2b. 音生成モデル（bgm / ambience / sfx / foley）

ローカル優先。モデルは初回 generate で Hugging Face から取得し、プロセス内に保持する。

```bash
pip install 'transformers>=4.40'     # musicgen（bgm・最大30秒・CC-BY-NC 4.0）
pip install 'diffusers>=0.31'        # stable_audio（ambience/sfx/foley・最大約47秒）
huggingface-cli login                # stable-audio-open-1.0 は gated（要同意＋ログイン）
```

- モデルは `SAL_MUSICGEN_MODEL` / `SAL_STABLE_AUDIO_MODEL` で差し替えられる。
- 依存を入れる前に配線を確かめたいときは `--provider stub`（決定的な合成・本物の音ではない）。
- `--provider` を明示すれば、その Provider が対応しない型は Route で即座に失敗する。
- stable_audio のサンプリング回数は `SAL_STABLE_AUDIO_STEPS`（既定 100）。CPU では
  1 ステップ約 3.2 秒かかるので、試し切りは 10〜20 で。
- `diffusers` が torchsde を要求する（スケジューラが import する）。無い場合は
  `pip install torchsde`。ただし**その木は使わない**——`CosineDPMSolverMultistepScheduler`
  が建てる BrownianTree は、この組み合わせ（diffusers 0.31 + torchsde 0.2.6 + Python 3.12）で
  `RecursionError` になる。Provider が増分の源を独立な正規へ差し替える（前へ進む掃引では
  重ならない区間の増分はそれで足りる）。生成物はこの差し替えの上で作られる。

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
| `SAL_LIBRARY_DIR` | 音響ライブラリ（既定は repo 直下 `library/`） |
| `SAL_PROJECTS_DIR` | 生成物の置き場（既定は repo 直下 `projects/`） |
| `SAL_MUSICGEN_MODEL` | bgm のモデル（既定 facebook/musicgen-small） |
| `SAL_STABLE_AUDIO_MODEL` | 音のモデル（既定 stabilityai/stable-audio-open-1.0） |
| `SAL_STABLE_AUDIO_STEPS` | stable_audio のサンプリング回数（既定 100） |
| `SAL_DEVICE` | 生成モデルのデバイス（既定 cpu） |
| `SAL_RESOLVE_MODEL` | Resolve のモデル（既定 claude-sonnet-4-5） |
