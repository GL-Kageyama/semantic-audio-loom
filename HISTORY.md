# HISTORY — 開発履歴

日付入りの変更経緯・過去の設計との比較・実測値はここに記録する。現在の情報は README / docs / SKILL を見る。

## 2026-08-29 — 実装一式（M0〜M3・資材分離・参照音声拡充）

### M0 — Provider スパイク（Tsukasa_Speech 確定）

- 作業ディレクトリ `/Users/user/sonic-loom-spike/`（venv=kokoro/chatterbox、venv_tsukasa=tsukasa）。
- Kokoro = 速度のみ・感情なし（切り捨て）。Chatterbox = exaggeration で強度反映（5 修正要）。
- **Provider は Tsukasa_Speech に確定**（ユーザー聴取で「圧倒的にいい」）。KotoDama プロンプト（自然言語の演技指示）→ 256 次元スタイル（timbre 128 + prosody 128）。
- **参照音声なしでも演技指示だけで声を生成できる**ことを実証（経路B）。
- モデル ~5GB（Top_ckpt 2GB / PLBERT 1.9GB / KTD 640MB）。日本語は `phonemize`（cutlet 経由）必須。
- 核心検証：抽象的 subtext 文の追記は破綻するが、subtext を具体的な抑揚指示（語尾の上げ下げ・ためらい・平坦）に変換する Resolve 経路なら明確に音に乗る（f0 実測：resolve_afraid 語尾上昇/mean325Hz vs resolve_indifferent 語尾下降/mean285Hz）。
- 声アイデンティティの制約：KotoDama プロンプト経路は女性バイアスが強い。
- 参照音声ライブラリ（老若男女 10 名）構築：VCTK（CC BY 4.0）若〜壮年 8 名 + Common Voice（CC0）老人 2 名。
- alpha/beta スイープで**確定 alpha=0.35, beta=0.7**（beta は「ピッチ演技のノブ」）。
- 複製 f0 の run 間分散は seed 固定で解決。境界話者 4 名は話者別 seed（`seeds.json`）で永続化。

### M1 — ウォーキングスケルトン

- 新リポジトリ `semantic-audio-loom/`（旧名 Sonic Loom。ブランド重複で改名）。7 段フロー（Validate → Route → Resolve → Generate → Normalize → Tag → Store）の Resolve 以外をつなぐ。
- パッケージ `semantic_audio_loom/`（config / types / providers / engine / skills）+ bin/（generate / regenerate）。
- E2E 実測：generate→regenerate で byte-identical（seed=42）。

### M2 — Resolve（価値の核心）

- LLM 呼び出しは SDK でなく stdlib urllib の直接 HTTP（anthropic 1.2.0 が temperature 引数を廃止して破綻したため）。`llm/client.py` が `/v1/messages` を直接叩く。
- Resolve の実体：subtext を抽象文でなく具体的な抑揚指示へ変換。Performance Spec に `prosody.intonation`（rising/falling/flat/wavering/neutral）を**スキーマ拡張で追加**。
- LLMResolver（既定）と RuleResolver（決定的写像・intonation=neutral・フォールバック）。
- M2 実測：同一台詞・同一 Direction で State だけ変えると Spec が変わる（返事が怖い→wavering vs どうでもいい→flat）。

### M3 — 一貫性検証

- mashiro を 2 シーン（朝 joy / 夜 anxiety）で生成、同一参照音声・同一キャラで f0 307.9Hz / 261.6Hz（差 46Hz は感情プロソディ、timbre は同一）。

### 資材の分離（ユーザー要望「キャラを再利用したい」）

- Step1 キャラ作り（`bin/character.py` → `characters/*.voice.yaml`）と Step2 声の生成（`bin/generate.py --character` → `projects/*/assets/`）を分離。
- 修正：resolve_rule が未指定 delivery を None で含めてスキーマ検証に落ちるバグを `_strip_none` で解決。

### 演技の振り付けと参照音声拡充（ユーザー要望）

- **演技資材**（`performances/*.direction.yaml`）：感情・声量・速度・delivery などの Direction を名前で再利用。`bin/performance.py`（init/validate/list）＋ `bin/generate.py --performance <name>`（CLI フラグで上書き）。
- **参照音声拡充**（`bin/reference.py`）：`synthesize`（ローカル生成・経路B・`--character` で voice.yaml の属性を入力）と `add`（著作権フリー音源の出典・ライセンス付き登録）。generate.py は既定で参照音声の欠落を検査し案内する。
- schemas 5 本化（performance_asset 追加）。

### 参照音声ライブラリを repo 内へ移設

- 以前は `資料/音声素材エンジン_構想/参照音声ライブラリ`（絶対パス）を config が参照していたが、clone で動かないため repo 直下 `references/` に本体（10 WAV + manifest.json + seeds.json）を移設。config.REFERENCE_LIB を repo 相対に変更。
- `requirements.txt` 追加。資料/側は検証産物（cloned/sweep/seed_sweep）だけ残す。

### リポジトリ構成の Claude Code 準拠

- 兄弟リポジトリ（elevate / distill-essence 等）の流儀に合わせ、CLAUDE.md / HISTORY.md / docs/ / skills/ / install.sh / .claude-plugin/ / .claude/skills（symlink）を整備。README は現行情報のみにスリム化し、履歴は HISTORY.md・深掘りは docs/ へ分離。
- 生成サンプルを `output*`（gitignore 済みスクラッチ）から `examples/mashiro-night/`（コミット対象）へ統合。

## 2026-08-29 — M4 蒸留（大量インプット → 資材）

- 手で埋める init の代わりに、物語・脚本・人物描写からキャラ（voice_profile）と演技（performance_asset）を自動生成する蒸留機構を追加。distill-essence-engine の蒸留（①理解→②選択→③翻訳）を音声資材向けに翻案。
- 二モード：`batch`（物語1つ → キャラ複数 × 演技複数）と `character`/`performance`（1入力 → 1資材）。`--synthesize` で元音声（経路B）も生成・登録、`--dry-run` で YAML 確認。
- ③翻訳の出力は schema の enum 制約（`pitch: very_low〜very_high` 等）。enum 外・必須欠落は手で直さず再生成（`_distill` が最大 3 回再試行）。
- `synthesize` の実体を `skills/reference.py` の `synthesize_reference` / `duration_sec` へ抽出し、`bin/reference.py` と `bin/distill.py` で共用。
- tests/ 新設（`test_distill.py`・モック LLM・11 件）+ conftest.py + requirements.txt に pytest 追加。
