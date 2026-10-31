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
| voice | `emotion`（必須） `intensity` `volume` `speed` `pitch` `breathiness` `delivery` `intonation` |
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

`--resolve rule` は翻訳しないので、英語にできるのは構造フィールド（`mood` `instrumentation`
など、もともと英語の語）と、英語で書かれた `situation` だけ。日本語の `situation` は
プロンプトへ足さず `subtext` に残す。Direction に日本語を直接書いた場合は、非英語が
プロンプトに残る旨を警告する（`--resolve llm` なら英語化される）。

### プロンプトは音の説明である（bgm）

生成モデルは「どんな音が鳴るか」を書いた文に条件づけられる。`60 BPM` や
`understated background score`、`instrumental, no vocals` のような属性の羅列は音の
説明ではないので、条件づけが薄れやすい（同じ seed・同じモデルで、羅列と説明文の
スペクトルを比べた測定は [HISTORY.md](../HISTORY.md) の M5 にある）。Rule 解決は
属性を音の側の語へ翻訳して、楽器を主語にした一文にする：

| Spec | プロンプトでの扱い |
| --- | --- |
| `instrumentation` | 主語の名詞（`felt piano` → `A felt piano piece`） |
| `role` | 修飾語（underscore → `understated`、theme → `melodic`） |
| `texture` / `arrangement.density: sparse` | 修飾語（`soft`、`sparse`） |
| `mood` | 接続した様子（`lonely and still`） |
| `tempo` | 形容（`slow` / `moderate` / `upbeat` / `fast`）。BPM の数値は書かない |
| `key` / `meter` | `in C minor, 3/4 time` |

`no vocals` のような否定は書かない。生成モデルは否定を演算しないので、`vocals` を
名指しするだけになる。楽器が無ければ `style` / `genre` を主語にし、それも無ければ
`A piece of music` になる。`loop` など音の説明でないフィールドは Spec に残るが、
プロンプトには入らない。

**楽器の名は具体に書く。** `strings` だけだと低弦の唸りになり、2kHz 以上が
−46 dB まで落ちる（歌う弦＝バイオリンが鳴らない）。`violins and cello` と名指すと
同じ seed・同じ尺で高域 −6 dB・重心 1018 Hz まで戻る（実測は
[HISTORY.md](../HISTORY.md)）。`pad` は名指ししても暗いままで、musicgen-small は
明るいパッドを出さない（`no_highs` が目印）。

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
- 依頼の尺が Provider の `max_seconds` を超えるときは、切ったことを stderr に出す
  （黙って短い資材を返さない）。切るのは Provider で、判定は Route が持つ。
- 環境変数：`SAL_MUSICGEN_MODEL`・`SAL_STABLE_AUDIO_MODEL`・`SAL_DEVICE`。

依存は `pip install 'transformers>=4.40'`（musicgen）/ `pip install 'diffusers>=0.31'`
（stable_audio）。どちらも重いので、コア（管理・検証・Resolve）には要らない。

### 声の混ぜ方（alpha / beta）

Tsukasa は参照音声の timbre ベクトルと、プロンプトから作った prosody ベクトルを
1 本の `ref_s` に連結して合成する。割合を決めるのが 2 つのノブ（`config.ALPHA` /
`config.BETA`、既定 0.35 / 0.7）。

| ノブ | 下げると | 上げると |
| --- | --- | --- |
| `alpha` | 参照音声の声質を保つ | 声質もプロンプト寄りになる |
| `beta` | **プロンプトの演技が乗る**・seed のばらつきも縮む | 参照音声に寄る・演技は seed の揺れに埋もれる |

- 既定（beta 0.7）では感情の一文が音にほぼ出ない（10 感情 × seed 5 で分かれない）。
  beta 0.3 では高覚醒（anger・joy）と低覚醒（neutral・sadness）の f0 が分かれるが、
  参照音声からの声質の距離は広がる。**演技と声質の引き換え**。
- 環境変数 `SAL_ALPHA` / `SAL_BETA` で振れる（測定用）。実際に使った値は
  生成物の `params.yaml` に残るので、再生成の照合は崩れない。
- ノブはプロセス全体に効く（1 本ごとには振れない）。人物や場面ごとに演技の強さを
  変えるには生成を分けて走らせる。

## 保存形式

`config.OUTPUT_FORMATS` が asset_type ごとの `(sample_rate, channels)` を持つ。

| Type | サンプルレート | チャンネル |
| --- | --- | --- |
| voice | 24kHz | mono |
| bgm / ambience / sfx / foley | 44.1kHz | 生成のまま（musicgen は mono、stable audio は stereo） |

Normalize はリサンプル・ピーク正規化（天井 0.95）・末尾フェードを行う。
`loop.enabled` の bgm / ambience には末尾フェードを掛けない（継ぎ目に無音ができるため）。
生成モデルは曲の途中から鳴り始めることがあるので、先頭が 0 でない波形には 2ms のランプを
掛けてプツッを消す（立ち上がりは鈍らせない。声とループ資材には掛けない）。
ラウドネス（LUFS）基準の正規化はミキサー（M6）の仕事で、まだ入っていない。
