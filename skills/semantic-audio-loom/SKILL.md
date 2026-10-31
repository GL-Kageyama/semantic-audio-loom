---
name: semantic-audio-loom
description: Semantic Audio Loom の音響素材エンジン。Context + Intent + State + Emotion + Direction から意味付き音響アセットを生成する（正典 5 種 voice/bgm/ambience/sfx/foley すべて対応）。台詞の裏の意味（subtext）まで反映した声、音楽・環境音・効果音・フォーリー、それらを貯める再利用ライブラリを扱う。
argument-hint: '(optional) キャラ名・演技名・台詞。例: /semantic-audio-loom キャラ mashiro・演技 anxious-night-call・台詞「……まだ、起きてる？」'
---

# semantic-audio-loom — 意味的音響アセット生成

音を単なるファイルでなく、意味・文脈・感情を持った生成・再利用可能な音響アセットとして扱うエンジン（正典 5 種 voice/bgm/ambience/sfx/foley）。設計の分かれ目は **Direction（監督＝意図）と Interpretation（俳優＝実現）の分離**。境界は type 別のモデル非依存 Spec（voice=Performance / bgm=Music / ambience・sfx・foley=Sound）。

## 資材モデル（再利用するもの / 使い捨てるもの）

| 資材 | 役割 | ツール | 場所 |
| --- | --- | --- | --- |
| 参照音声 | 声の実体 | `bin/reference.py` | `references/` |
| キャラ | 誰の声か | `bin/character.py` | `characters/*.voice.yaml` |
| 演技の振り付け | どう演じるか | `bin/performance.py` | `performances/*.direction.yaml` |
| 音響ライブラリ | 何度も使う音 | `bin/library.py` | `library/<type>/<name>.asset.yaml` |
| Sound Bible | 作品の音響スタイル | `bin/sound-bible.py` | `projects/<project>/sound-bible.yaml` |
| 生成音声 | 産物（使い捨て） | `bin/generate.py` / `bin/asset.py` | `projects/*/assets/` |

## ワークフロー

1. **参照音声が足りていれば確認** — `bin/reference.py list`。足りない声は `synthesize <key> --character <name>`（ローカル生成）か `add <wav> <key> --license …`（著作権フリー音源）で拡充。
2. **キャラを作る**（誰の声か）— `bin/character.py init <name>` → `characters/<name>.voice.yaml` を編集（`reference_audio` で参照音声を指定）。
3. **演技を定義する**（どう演じるか）— `bin/performance.py init <name>` → `performances/<name>.direction.yaml` を編集（emotion / intensity / volume / speed / delivery / situation / subtext）。
   **狙った向きに頼れるのは `speed`**（5 語が単調・1.74〜1.80 倍）。`emotion` は neutral より
   高い声になる（+4〜+26 Hz）が、**感情どうしは書き分けられない**（隣どうしは 3 Hz 以下・
   `delivery` を足しても離れない）。`intensity` は 2 段。`delivery` は 12 語のうち
   `aggressive`/`desperate`/`cold`/`flat` の 4 語だけ動き、残りは同じ声。`pitch` は
   **下げる語だけ**（上がる語は無い）。`volume` は声の大きさを変えない（`shout` だけ
   f0 +9.6・長さ +0.13 秒、energy は下がる。ミックスの `gain_db` が作る）。`intonation` の
   5 語もほぼ同じ声で、語尾の傾きは名前どおりにならない — 詳細は `docs/resolve.md`
   「どの欄が、声を動かすか」。`subtext` は `--resolve rule` では音に載らず（Provider の
   散文がその欄を読まない）、`--resolve llm` でも効くのは変換後の `intensity` の段だけ。
   **台詞の文末の記号は欄より強く効く**：`？` は f0 +16.3 Hz・`！` は +39.3 Hz（5/5）、
   感情の欄とは足し算になる。記号なしは語尾が落ちる。**効きは行の形で縮む**
   （14 文字 +38.9・24 文字 +13.2 Hz。**途中に句点が 1 つあると 9 文字でも +15.2 Hz**
   まで落ちる——つなぎは読点にする）。**「！」を欄で出そうとしない。**
4. **声を生成する** — `bin/generate.py --character <キャラ> --performance <演技> --line <台詞>`。

## 声の生成

```bash
bin/generate.py --character mashiro --performance anxious-night-call \
    --project demo --scene night \
    --line "……まだ、起きてる？" --name mashiro_night
```

- キャラ（誰）と演技（どう演じる）は独立に再利用できる。同じキャラで別の演技、別のキャラで同じ演技。
- 演技資材は CLI フラグで上書きできる（`--emotion joy` など未指定分は資材の値を引き継ぐ）。
- `--resolve llm`（既定）で subtext を具体的な抑揚（語尾 intonation）へ変換。`--resolve rule` は決定的写像（LLM なし）。
- 台詞は日本語。`--seed` で再現可能。

## 音の生成（bgm / ambience / sfx / foley）

```bash
bin/asset.py --type bgm --project demo --name lonely-room \
    --sound role=underscore --sound mood=lonely --duration 20
bin/asset.py --type ambience --project demo --name station-night \
    --sound environment="empty train station" --sound time=night --duration 30
```

- Direction は `--sound key=value`（カンマで配列、`{...}` で JSON）。**意味フィールド**を書く
  （bgm は mood/instrumentation/tempo、ambience は environment/time/weather、
  sfx は event/object、foley は action）。
- `--resolve llm`（既定）が抽象語を「何が・どこで・どの材質で鳴るか」と英語プロンプトへ具体化。
- 既定 Provider は bgm=`musicgen`、ambience/sfx/foley=`stable_audio`（ローカル）。
  依存が無い環境では `--provider stub` で配線だけ確認できる（本物の音は出ない）。
- 何度も使う音は `--save-library <name>` で `library/` へ。`bin/library.py search <語>` で探せる。
- 作品の既定は `bin/sound-bible.py init <project>` → `projects/<project>/sound-bible.yaml`。
- 声・bgm・sfx を 1 本にするときは `bin/mix.py --file mix.yaml`（層は bed / voice / hit、
  voice の間だけ bed が沈む）。生成済みの WAV を時刻と利得で束ねるだけで、生成はしない。
  出力はステムの最大チャンネル数（mono の声は真ん中、ステレオの sfx は左右を保つ）。
- できた音は `bin/probe.py <wav>` で測る。`起伏`（10ms 包絡の最大−中央値）が高ければ
  点で鳴る音、数 dB なら持続音——sfx に頼んだ音が点で鳴ったかはここで見る。

## 実行環境

- 声の生成には Tsukasa_Speech（~5GB）と `SAL_TSUKASA_DIR`、音の生成には transformers /
  diffusers とモデル（初回 DL）が要る。詳細は `docs/setup.md`。
- 参照音声の欠落は generate.py が既定で検知し、拡充コマンドを案内する。

## 言語（Language Mode）

実行言語は `--lang {en,ja,zh}`（`$ARGUMENTS.lang`）> 環境変数 `SAL_LANG` > 既定 ja。ユーザーの依頼言語に合わせ `--lang` を渡す。ただし台詞＝生成音声は Tsukasa が日本語 TTS のため常に日本語。README/docs は日本語のまま。

## 深掘り

- `docs/asset-types.md` — 正典 5 種とロードマップ（Phase 1〜5）
- `docs/asset-generation.md` — 音の生成（Spec・Direction・Provider）
- `docs/library.md` — 再利用ライブラリ
- `docs/sound-bible.md` — Sound Bible
- `docs/resolve.md` — subtext を音に乗せる Resolve（声の核心）
- `docs/distill.md` — 蒸留（大量インプット → キャラ/演技）
- `docs/loudness.md` — 声量の三層分業
- `docs/reference-voices.md` — 参照音声と拡充
