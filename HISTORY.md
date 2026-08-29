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
- tests/ 新設（`test_distill.py`・モック LLM・10 件）+ conftest.py + requirements.txt に pytest 追加。

## 2026-08-29 — Asset Type 正典化（構想 §4 の 5 種）

- 音を声に閉じないよう、構想 §4 の 5 Asset Type（voice / bgm / ambience / sfx / foley）を正典として明文化。`types.ASSET_TYPES`（定数）＋ `schemas/asset_type.schema.json`（enum）＋ `validate_intent` の enum 外拒否で、将来スコープを閉じない。
- 実装済みは Phase 1 の `voice` のみ。ambience/sfx（Phase 2）・bgm（Phase 3）は将来スコープで、生成モデル・Resolve 経路・Sound Bible は未実装。詳細は docs/asset-types.md。

## 2026-08-29 — 多言語化（i18n / en・ja・zh）

- CLI 文言と LLM プロンプトを 2 層（`locales/{lang}.json` ＋ `prompts/{lang}.json`）で現地化。対象 en/ja/zh、既定 ja。言語解決は `--lang` > `SAL_LANG` > ja（未対応言語は警告して ja へ）。新規文言は `semantic_audio_loom/i18n.py` の `_t()`（引数名 `name`・`default` は日本語の安全弁）で解決。
- 固定列挙値（enum）は英語のまま、自由テキスト（situation/subtext/キャラ表示名）は `--lang` の言語で出力（プロンプト末尾に出力言語ディレクティブ）。台詞（`--line`）は Tsukasa が日本語 TTS のため常に日本語（領域事実＝i18n 対象外）。
- エンジン結線：resolve / distill / llm.client / engine に `lang` を追加。波括弧衝突回避のため、JSON スキーマ例を含む system プロンプトは `.format()` せず、`.format()` するのは `resolve.user` と `distill.retry` のみ。
- **経緯**：当初は並列リポジトリ（wisdom/elevate）と同じ「フル3層（locales+prompts+docs ミラー・既定 en）」を検討したが、(1) Tsukasa が日本語 TTS のため音声出力は日本語のまま＝非日本語話者が主対象になる可能性が低く docs 翻訳の実利が薄い、(2) 既定 en だと日本語 README と CLI 出力が非整合——の2点から「プロンプト＋CLI のみ・既定 ja・README/docs は日本語のまま」に絞った。docs ミラーツリーは作らない。
- tests/test_i18n.py 追加（言語解決の優先順位・3言語キー整合・en/zh プロンプトに日本語かな漏れなし・モック LLM で3言語完走・CLI `--lang` スモーク）。テスト 24 件。

## 2026-08-30 — 語尾の「ぶった斬れ」対策（末尾フェード）

- 実測：Tsukasa の拡散出力は release を持たない音素（「る」「た」などの短母音・促音系）だと
  最終フレームを有声のまま終端させる（末尾 RMS 0.16〜0.27・decay 0ms）。長母音
  （「う」「い」）は自然減衰（decay 500〜620ms）。要の一打は文末＝切断位置に置かれるため、
  重要な語ほど「余韻がぶった斬れる」。
- B（余韻の回復）は不発：`rate_of_speech` を 1.0→0.75 に下げても decay は 0ms のまま。
  `intonation=falling`（"trailing off" 追加）も sadness 感情句に既に含まれており変化なし。
- 方針 A（末尾フェード）で確定：`normalize` に半ハン余弦フェード（`TAIL_FADE_MS=30ms`）を
  追加。クリック除去に留め、余韻そのものは復元しない（モデルが release を出さないため）。
  自然減衰した波形（末尾無音）には実質 no-op。
- tests/test_normalize.py 追加（3件）。
