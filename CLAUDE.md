# semantic-audio-loom — プロジェクト指示

## 文書ルール

開発履歴（日付入りの変更経緯・過去の設計との比較・過去の実測値など）は **README / SKILL / examples に書かない**。履歴は `HISTORY.md` に一元化する。

README / SKILL には**現在の情報だけ**を書く。現在の機能・CLI・設計の根拠（日付なしの短い理由）は OK。「以前は X だったが Y に変えた」のような経緯が必要なら HISTORY.md へ。

**置き場所**：
- `README.md` … 現在の機能・資材モデル・CLI・構成（概要のみ。深掘りは docs/ へのリンク）
- `docs/` … README の深掘り（`resolve.md` = Resolve/subtext・`asset-types.md` = 正典5種とロードマップ・`asset-generation.md` = 音の生成・`library.md` = 再利用ライブラリ・`sound-bible.md` = 作品の音響スタイル・`distill.md` = 蒸留・`loudness.md` = 声量三層分業・`reference-voices.md` = 参照音声と拡充・`setup.md` = セットアップ・`usage.md` = 全CLI）
- `HISTORY.md` … 開発履歴（M0〜M4・実測値）
- `skills/semantic-audio-loom/SKILL.md` … facade スキル（現在の使い方のみ）
- `.claude/skills/` … ルート `skills/` への symlink（プロジェクト内検出用。インストール不要）
- `.claude-plugin/` … プラグイン配布定義。`install.sh` が従来の symlink 方式（global/local）

## 固定方針（変更しない）

- **Direction（監督＝意図）と Interpretation（俳優＝実現）の分離**。境界はモデル非依存の **Spec**（voice=Performance / bgm=Music / ambience・sfx・foley=Sound）。`subtext`（台詞の裏の意味）と、音では抽象語→具体的な音の記述が差別化点。
- **subtext は抽象文のままでは音に乗らない**。Resolve が必ず具体的な抑揚指示（語尾 `prosody.intonation` など）へ変換してから Provider に渡す。
- **声量は三層分業**：Direction `volume` → Interpretation `loudness.effort` → Mixing ピーク正規化。ゲインを上げても「張り」は増えない。
- **資材の分離**：再利用するもの（参照音声＝声の実体・キャラ＝誰の声か・演技＝どう演じるか）と、使い捨てるもの（生成音声 = `projects/*/assets/`）を混ぜない。
- **seed 決定論**：同じ seed で byte-identical 再生成（regenerate が保存済み Spec を再利用し、LLM を再呼び出ししない）。
- **Asset Type は 5 種（voice / bgm / ambience / sfx / foley）を正典とし、声に閉じない**。5 種すべてに生成経路がある（voice=tsukasa / bgm=musicgen / ambience・sfx・foley=stable_audio / テスト用 stub）。7 段フローは共通で、Validate・Resolve・Metadata・Normalize・Route が asset_type で分岐する。正典の実体は `types.ASSET_TYPES` と `schemas/`、詳細は `docs/asset-types.md`。
- **モデル向けプロンプトは英語**。`Music Spec` / `Sound Spec` の `prompt` は生成モデル（MusicGen / Stable Audio）が読むので、Resolve は `--lang` に関わらず英語で書く。`subtext` などの自由テキストだけ `--lang` に従う。
- **i18n baseline（2層）**：新規の CLI 文言・LLM プロンプト・YAML テンプレートは直書きせず、`locales/{lang}.json`（CLI/UI）と `prompts/{lang}.json`（LLM）の2層で解決する。対象 en/ja/zh、既定 ja（`--lang` > `SAL_LANG` > ja、未対応は警告して ja）。固定列挙値（emotion/pitch 等の enum）は全言語で英語のまま、自由テキスト（situation/subtext/キャラ表示名）は `--lang` の言語で出力、台詞（`--line`）は Tsukasa が日本語 TTS のため常に日本語。docs ミラーは作らない（README/docs は日本語のまま）。

## テスト

`pytest tests/`。重いモデルは使わず、非 voice は `--provider stub` で 7 段フロー全体を通す
（`tests/test_sound_assets.py`）。テスト用の venv は `/Users/user/sonic-loom-spike/venv_tsukasa`
（torch・numpy・jsonschema・pytest が入る。素の python3 では jsonschema が無いことがある）。

## 壊してはいけないもの

- Resolve の LLM 応答が崩れたら、手で直さず再生成する。
- Provider（Tsukasa）は初回 generate 時に遅延ロードし、プロセス内で保持する（~5GB・import ~1 分）。

## Git

- `git push` はユーザーが明示的に依頼した時だけ。依頼なしの push は禁止。
- コミットメッセージ末尾に `Co-Authored-By: Claude <noreply@anthropic.com>` を付ける。
- **`git add -A` は使わない。** 触ったパスだけを add する（他の未コミット変更を巻き込まない）。
- **音声と画像は Git LFS に入れる**：`*.wav` `*.mp3` `*.m4a` `*.flac` `*.ogg` `*.mp4` `*.png` `*.jpg` `*.jpeg`（規則は `.gitattributes`）。
  **テキスト（コード・YAML・Markdown・TSV・JSON）は対象外。** 新しいバイナリ形式を追うときは `.gitattributes` に 1 行足す。
  ⚠️ `git-lfs` の無い clone はポインタを降ろす。`git lfs pull` が要る。
