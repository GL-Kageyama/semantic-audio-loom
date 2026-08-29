# semantic-audio-loom — プロジェクト指示

## 文書ルール

開発履歴（日付入りの変更経緯・過去の設計との比較・過去の実測値など）は **README / SKILL / examples に書かない**。履歴は `HISTORY.md` に一元化する。

README / SKILL には**現在の情報だけ**を書く。現在の機能・CLI・設計の根拠（日付なしの短い理由）は OK。「以前は X だったが Y に変えた」のような経緯が必要なら HISTORY.md へ。

**置き場所**：
- `README.md` … 現在の機能・資材モデル・CLI・構成（概要のみ。深掘りは docs/ へのリンク）
- `docs/` … README の深掘り（`resolve.md` = Resolve/subtext・`loudness.md` = 声量三層分業・`reference-voices.md` = 参照音声と拡充）
- `HISTORY.md` … 開発履歴（M0〜M3・資材分離・参照音声拡充・実測値）
- `skills/semantic-audio-loom/SKILL.md` … facade スキル（現在の使い方のみ）
- `.claude/skills/` … ルート `skills/` への symlink（プロジェクト内検出用。インストール不要）
- `.claude-plugin/` … プラグイン配布定義。`install.sh` が従来の symlink 方式（global/local）

## 固定方針（変更しない）

- **Direction（監督＝意図）と Interpretation（俳優＝実現）の分離**。境界はモデル非依存の **Performance Spec**。`subtext`（台詞の裏の意味）が差別化点。
- **subtext は抽象文のままでは音に乗らない**。Resolve が必ず具体的な抑揚指示（語尾 `prosody.intonation` など）へ変換してから Provider に渡す。
- **声量は三層分業**：Direction `volume` → Interpretation `loudness.effort` → Mixing ピーク正規化。ゲインを上げても「張り」は増えない。
- **資材の分離**：再利用するもの（参照音声＝声の実体・キャラ＝誰の声か・演技＝どう演じるか）と、使い捨てるもの（生成音声 = `projects/*/assets/`）を混ぜない。
- **seed 決定論**：同じ seed で byte-identical 再生成（regenerate が保存済み Spec を再利用し、LLM を再呼び出ししない）。

## テスト

`pytest tests/`（tests/ は未整備。整備次第ここに記載）。

## 壊してはいけないもの

- Resolve の LLM 応答が崩れたら、手で直さず再生成する。
- Provider（Tsukasa）は初回 generate 時に遅延ロードし、プロセス内で保持する（~5GB・import ~1 分）。

## Git

- `git push` はユーザーが明示的に依頼した時だけ。依頼なしの push は禁止。
- コミットメッセージ末尾に `Co-Authored-By: Claude <noreply@anthropic.com>` を付ける。
