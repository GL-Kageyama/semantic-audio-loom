# 音の生成 — bgm / ambience / sfx / foley

声と同じ 7 段フロー（Validate → Route → Resolve → Generate → Normalize → Tag → Store）
を通る。違うのは Resolve の出す Spec だけ。

| Asset Type | Direction | Spec | 既定 Provider |
| --- | --- | --- | --- |
| voice | Performance Direction | Performance Spec | tsukasa |
| bgm | Music Direction | Music Spec | musicgen |
| ambience | Sound Direction | Sound Spec | stable_audio |
| sfx | Sound Direction | Sound Spec | stable_audio |
| foley | Sound Direction | Sound Spec | stable_audio |

Spec の正典は `schemas/`：`music_spec.schema.json`・`sound_spec.schema.json`。

## 使い方

```bash
# BGM（20 秒。Direction は key=value。カンマで配列）
bin/asset.py --type bgm --project demo --name lonely-room \
    --sound role=underscore --sound mood=lonely,sparse \
    --sound instrumentation=solo_piano --sound tempo='{"bpm": 60}' --duration 20

# 環境音（ステレオのまま保存）
bin/asset.py --type ambience --project demo --name station-night \
    --sound environment="empty train station" --sound time=night \
    --sound space=indoor --duration 30

# 効果音
bin/asset.py --type sfx --project demo --name door-close \
    --sound event="heavy wooden door closing" --sound distance=near --duration 3

# フォーリー
bin/asset.py --type foley --project demo --name cloth-rustle \
    --sound action="a person shifting under a blanket" --sound surface=futon --duration 2
```

生成物は `projects/<project>/assets/<scene>/<name>.wav` と `.params.yaml`
（voice と同じ場所の規則）。`--sound-file direction.yaml` で Direction をまとめて渡せる。

## Direction のフィールド

| Type | フィールド |
| --- | --- |
| bgm | `role` `genre` `mood` `style` `tempo` `key` `meter` `instrumentation` `arrangement` `texture` `energy` `duration` `loop` `negative` `prompt` |
| ambience | `environment`（必須） `location` `time` `weather` `space` `density` `movement` `loop` `duration` `mood` `style` |
| sfx | `event` か `object`（どちらか必須） `material` `distance` `intensity` `duration` |
| foley | `action`（必須） `object` `surface` `contact` `duration` |

`role` は theme / underscore / jingle / loop / stinger。`duration` は秒。

## Resolve（意味 → 音の記述）

- `--resolve llm`（既定）… 抽象語（「不穏」「切ない」）を、何が・どこで・どの距離で・
  どの材質で鳴るかへ具体化し、モデル向けの**英語プロンプト**を書く。
- `--resolve rule` … 構造フィールドをそのまま Spec へ移し、プロンプトを決定的に組み立てる
  （LLM なし）。`prompt` を自分で書いた場合はそれをそのまま使う。
- LLM が失敗したら Rule へフォールバックする（voice と同じ）。

プロンプトはモデル向けなので**常に英語**。`subtext` などの自由テキストだけ `--lang` に従う。

## Provider（ローカル優先）

| Provider | 対象 | モデル | 長さ | ライセンス |
| --- | --- | --- | --- | --- |
| `musicgen` | bgm | `facebook/musicgen-small`（transformers） | 最大 30 秒・32kHz mono | CC-BY-NC 4.0 |
| `stable_audio` | ambience / sfx / foley / 短い bgm | `stabilityai/stable-audio-open-1.0`（diffusers） | 最大約 47 秒・44.1kHz stereo | Stability AI Community License |
| `stub` | 全 5 種 | なし（決定的な合成） | 最大 8 秒 | — |

- `stable_audio` は **gated**。Hugging Face でライセンスに同意し `huggingface-cli login` する。
- `stub` は配線・保存形式・ライブラリの確認用。本物の音は出ない。
- `--provider` で明示できる。Provider の `capabilities()["asset_types"]` に無い型を
  頼むと Route が即座に失敗する（生成してから気づかない）。
- 環境変数：`SAL_MUSICGEN_MODEL`・`SAL_STABLE_AUDIO_MODEL`・`SAL_DEVICE`。

依存は `pip install 'transformers>=4.40'`（musicgen）/ `pip install 'diffusers>=0.31'`
（stable_audio）。どちらも重いので、コア（管理・検証・Resolve）には要らない。

## 保存形式

`config.OUTPUT_FORMATS` が asset_type ごとの `(sample_rate, channels)` を持つ。

| Type | サンプルレート | チャンネル |
| --- | --- | --- |
| voice | 24kHz | mono |
| bgm / ambience / sfx / foley | 44.1kHz | 生成のまま（musicgen は mono、stable audio は stereo） |

Normalize はリサンプル・ピーク正規化（天井 0.95）・末尾フェードを行う。
`loop.enabled` の bgm / ambience には末尾フェードを掛けない（継ぎ目に無音ができるため）。
ラウドネス（LUFS）基準の正規化はミキサー（M6）の仕事で、まだ入っていない。
