# Semantic Audio Loom

Context + Intent + State + Emotion + Performance Direction → 意味的音声アセット。

台詞の「裏の意味（subtext）」まで反映した音声を生成するエンジン。
設計の分かれ目は **Direction（監督＝意図）と Interpretation（俳優＝実現）の分離** と、
その境界に置くモデル非依存の **Performance Spec**。

## 資材の分離（再利用の設計）

資材を「再利用するもの」と「使い捨てるもの」に分ける：

| 資材 | ツール | 場所 | 管理 |
| --- | --- | --- | --- |
| **参照音声**（声の実体） | `bin/reference.py` | 参照音声ライブラリ | 拡充・共有（出典/ライセンス記録） |
| **キャラ**（誰の声か） | `bin/character.py` | `characters/<name>.voice.yaml` | 再利用・永続 |
| **演技の振り付け**（どう演じるか） | `bin/performance.py` | `performances/<name>.direction.yaml` | 再利用・永続 |
| **生成音声**（産物） | `bin/generate.py` | `projects/<project>/assets/<scene>/` | 使い捨て・再生成可 |

- **キャラ**（声の持ち主）と**演技の振り付け**（演じ方）は独立に再利用できる。
  同じキャラで別の演技、別のキャラで同じ演技、どちらも名前で組み合わせられる。
- **参照音声**は足りない声を `bin/reference.py` で拡充できる（ローカル生成 or 著作権フリー音源の登録）。
- 生成した音声はキャラ/演技資材と混ぜず、プロジェクトごとの `assets/` に分離する。

```
キャラ作り（誰が）       演技の振り付け（どう演じるか）
    characters/              performances/
        ↓                          ↓
        └────── 声の生成（bin/generate.py）──────┘
                     ↓
         projects/<project>/assets/<scene>/  （wav + params）
                     ↑
     参照音声ライブラリ（声の実体・足りなければ bin/reference.py で拡充）
```

## 状態

- **M0 完了** — 技術検証（Tsukasa_Speech 確定、2 経路スタイル合成、alpha/beta ノブ、seed 決定論）。
- **M1 完了** — ウォーキングスケルトン。7 段フローの Resolve 以外を全通し、seed 固定で再生成（byte-identical）。
- **M2 完了** — Resolve（価値の核心）。Direction ＋ State ＋ Scene ＋ Dialogue → LLM → Performance Spec。subtext を具体的な抑揚指示（語尾 intonation）へ変換。
- **M3 完了** — 一貫性検証。参照音声（経路A）で声を固定し、同一キャラの声が複数シーンで保たれることを確認。

## 構成

```
characters/                     # キャラ資材（再利用・永続）
  mashiro.voice.yaml
performances/                   # 演技資材（再利用・永続）
  anxious-night-call.direction.yaml
references/                     # 参照音声ライブラリ（声の実体・10 名 + manifest.json + seeds.json）
projects/<project>/assets/      # 生成資材（使い捨て・再生成可）
semantic_audio_loom/
  config.py        Tsukasa/参照音声ライブラリ/キャラ/演技ライブラリのパス（環境変数で上書き可）
  types.py         GenerationIntent / GenerationRequest / Audio / AudioAsset
  providers/       Seam の下側。base(契約) + tsukasa(実体)
  engine/          validate / route / resolve / normalize / metadata / store / engine
  llm/             Resolve 用の最小 Claude API クライアント（Anthropic 互換 HTTP）
  skills/          character_voice（キャラ名解決）/ performance（演技名解決）/ reference（参照音声の拡充と解決）
bin/
  reference.py     参照音声の拡充（list / synthesize / add）
  character.py     キャラ作り（init / validate / list）
  performance.py   演技の振り付け（init / validate / list）
  generate.py      声の生成（キャラ + 演技 + 台詞 → wav + params）
  regenerate.py    params.yaml → 保存済み Spec・seed で再生成（再現性確認）
schemas/           5 スキーマ（voice_profile / performance_direction / performance_spec / performance_asset / character_state）
```

## 7 段フロー（声の生成）

```
Validate → Route → Resolve → Generate → Normalize → Tag → Store
```

- **Resolve**（M2 の核心）：Direction（監督）と State / Scene / Dialogue を LLM が解釈し、
  Performance Spec（俳優）へ解決する。subtext は抽象文のままでは音に乗らないため、
  必ず具体的な抑揚指示（語尾 `prosody.intonation` など）へ変換する。
- **Provider**（Tsukasa）：Spec のうち反映できる controls（emotion / delivery / 声量 / 速度 / 語尾）を
  KotoDama 散文へ変換して合成する。emphasis / breath / pauses の構造化制御は共通欠落。

## セットアップ（クローンから動くまで）

リポジトリ内で完結するもの（コード・キャラ・演技・参照音声）と、外部に置くもの（モデル・依存）を分ける：

```bash
# 1. Python 依存（コアだけでよければ numpy/PyYAML/jsonschema のみ）
pip install -r requirements.txt

# 2. Tsukasa_Speech チェックアウト（生成実行時のみ・モデル ~5GB は外部）
git clone https://github.com/... / Tsukasa_Speech を取得し、SAL_TSUKASA_DIR で指す
export SAL_TSUKASA_DIR=/path/to/tsukasa

# 3. Resolve の LLM（--resolve llm 時・既定）
export ANTHROPIC_AUTH_TOKEN=...      # または ANTHROPIC_API_KEY=...
export ANTHROPIC_BASE_URL=...        # ゲートウェイ。モデルは SAL_RESOLVE_MODEL で変更可
```

- キャラ（`characters/`）・演技（`performances/`）・参照音声（`references/`）は**同梱済み**。
  クローンすれば `bin/character.py list` や `bin/reference.py list` がそのまま動く。
- `--resolve rule`（決定的写像）なら LLM なしで Spec まで生成できる（音声合成は Tsukasa が要る）。
- 参照音声を外部に置く場合は `SAL_REFERENCE_LIB` で上書き（既定は repo 直下 `references/`）。

## 使い方

```bash
# Step 0 — 参照音声の拡充（足りない声があるとき）
bin/reference.py list                                    # 登録済み参照音声一覧
bin/reference.py synthesize elderly_man --character mashiro   # ローカル生成（経路B）
bin/reference.py add my_voice.wav old_woman --gender F --age sixties \
    --license "CC0" --source "Common Voice"               # 著作権フリー音源を登録

# Step 1 — キャラ作り（一度だけ）
bin/character.py init mashiro            # characters/mashiro.voice.yaml を生成
bin/character.py validate mashiro        # スキーマ検証
bin/character.py list                    # 登録済みキャラ一覧

# Step 1.5 — 演技の振り付け（再利用する演じ方を定義）
bin/performance.py init anxious-night-call
bin/performance.py validate anxious-night-call
bin/performance.py list

# Step 2 — 声の生成（キャラ + 演技を名前で再利用）
bin/generate.py --character mashiro --performance anxious-night-call \
    --project demo --scene night \
    --line "……まだ、起きてる？" --name mashiro_night
# 演技資材を CLI フラグで上書きも可（--emotion joy など未指定分は資材の値を引き継ぐ）
```

- `--resolve llm`（既定）で Resolve を LLM に、`--resolve rule` で決定的写像（API なし）に。
- `--situation` と `--state-file`（character_state の YAML）が subtext 推論の入力。
  `--subtext` で人間が裏の意味を直接指定もできる。
- 台詞は日本語（Tsukasa は `phonemize` で読みへ変換）。`--seed` で再現可能。

再生成（保存済み Spec を再利用・LLM は呼ばない）:

```bash
bin/regenerate.py projects/demo/assets/morning/mashiro_morning.params.yaml \
    --out-dir output_regen
```

## 声量（loudness）の三層分業

「声を大きくしたい」を単一のボリュームで済ませない：

| レイヤ | フィールド | 何を表すか |
| --- | --- | --- |
| Direction（意図） | `performance.volume` | 演出上の「ささやく／叫ぶ」 |
| Interpretation（実現） | `loudness.effort` | 声帯の張り・努力（張り） |
| Mixing（量） | ピーク正規化 | 再生音量の統一（張りには非関与） |

Direction の `volume` は Resolve が `loudness.effort`（relaxed / normal / projected / strained）へ解決し、
Mixing は `normalize.py` のピーク正規化のみ。**ゲインを上げても「張り」は増えない**
（M0 実測：angry rms 0.086 vs sad 0.055 は音量でなく演技）。

## 弱い声への方針

特定の声（例：男性老人）が弱い場合、**使用者が声を拡充して参照に指定する**のが既定。
開発者が全声を揃えない。足りない声は `bin/reference.py` で `references/` に追加し、
`.voice.yaml` の `reference_audio` で話者キーかパスを指定する。

- `bin/reference.py synthesize <key> --character <name>` … ローカル生成（経路B・参照不要）
- `bin/reference.py add <wav> <key> --license … --source …` … 著作権フリー音源の登録
