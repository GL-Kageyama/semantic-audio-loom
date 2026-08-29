# Semantic Audio Loom

Context + Intent + State + Emotion + Performance Direction → 意味的音響アセット。

音を単なるファイルではなく、意味・文脈・感情を持った生成・再利用可能な音響アセットとして
扱うエンジン。正典は 5 種（voice / bgm / ambience / sfx / foley）、実装は Phase 1 の voice。

声の設計の分かれ目は **Direction（監督＝意図）と Interpretation（俳優＝実現）の分離** と、
その境界に置くモデル非依存の **Performance Spec**。台詞の「裏の意味（subtext）」まで
反映するのが、テキスト読み上げとの決定的な差。

## 資材の分離（再利用の設計）

再利用するもの（参照音声・キャラ・演技）と、使い捨てるもの（生成音声）を分ける。

| 資材 | ツール | 場所 |
| --- | --- | --- |
| 参照音声（声の実体） | `bin/reference.py` | `references/` |
| キャラ（誰の声か） | `bin/character.py` | `characters/<name>.voice.yaml` |
| 演技の振り付け（どう演じるか） | `bin/performance.py` | `performances/<name>.direction.yaml` |
| 生成音声（産物） | `bin/generate.py` | `projects/<project>/assets/<scene>/` |
| 場面（複数人物を間で合成） | `bin/scene.py` | `scene.yaml` → `projects/<project>/assets/<scene>/` |

キャラと演技は独立に再利用でき、名前で組み合わせられる。生成音声はキャラ/演技資材と
混ぜず、プロジェクトごとに分離する。

## 状態

M0（Provider 確定）〜 M4（蒸留）まで完了。履歴・実測値は [HISTORY.md](HISTORY.md)。

## Asset Type（スコープ）

音を声に閉じない。正典 5 種（**voice / bgm / ambience / sfx / foley**）のうち、実装は
Phase 1 の `voice` のみ。残り 4 種は将来スコープ。[docs/asset-types.md](docs/asset-types.md)。

## クイックスタート

```bash
pip install -r requirements.txt          # 依存（コアのみ。生成は別途 Tsukasa が要る）

bin/reference.py list                    # 登録済み参照音声
bin/character.py list                    # 登録済みキャラ
bin/performance.py list                  # 登録済み演技

bin/generate.py --character mashiro --performance anxious-night-call \
    --project demo --scene night \
    --line "……まだ、起きてる？" --name mashiro_night
```

セットアップの詳細（Tsukasa・LLM の設定）は [docs/setup.md](docs/setup.md)、
全コマンドは [docs/usage.md](docs/usage.md)。

## 多言語対応（i18n）

CLI 文言と LLM プロンプトは **en / ja / zh** の 2 層（`locales/` ＋ `prompts/`）で現地化する。
既定は **ja**。`--lang {en,ja,zh}` フラグか環境変数 `SAL_LANG` で切り替え（`--lang` が優先）。

```bash
bin/character.py --lang en list     # 英語の CLI 文言
SAL_LANG=zh bin/distill.py --dry-run …   # 中国語のプロンプト
```

- 固定列挙値（emotion / pitch / age などの enum）は全言語で英語のまま。
- 自由テキスト（situation / subtext / キャラ表示名）は `--lang` の言語で出力。
- 台詞（`--line`）は **常に日本語**（Tsukasa が日本語 TTS のため。領域事実）。

README・docs は日本語のまま（翻訳ミラーは用意しない）。

## 7 段フロー

```
Validate → Route → Resolve → Generate → Normalize → Tag → Store
```

核心は **Resolve**（Direction → Performance Spec。voice のみ）。詳細は [docs/resolve.md](docs/resolve.md)。

## 構成

```
characters/  performances/  references/   # 再利用資材（キャラ・演技・参照音声）
projects/    examples/                     # 生成産物・サンプル
semantic_audio_loom/                      # パッケージ（config/types/providers/engine/llm/skills）
bin/          schemas/     docs/           # CLI / JSON Schema / 深掘り
skills/       .claude-plugin/              # facade スキル / プラグイン配布
```

## ドキュメント

| 文書 | 内容 |
| --- | --- |
| [docs/resolve.md](docs/resolve.md) | Resolve・subtext（価値の核心） |
| [docs/asset-types.md](docs/asset-types.md) | 正典 5 種とロードマップ（Phase 1〜5） |
| [docs/distill.md](docs/distill.md) | 蒸留（大量インプット → キャラ/演技） |
| [docs/loudness.md](docs/loudness.md) | 声量の三層分業 |
| [docs/scene.md](docs/scene.md) | シーン合成（複数人物×間） |
| [docs/reference-voices.md](docs/reference-voices.md) | 参照音声と拡充・弱い声への方針 |
| [docs/setup.md](docs/setup.md) | セットアップ（Tsukasa・LLM・環境変数） |
| [docs/usage.md](docs/usage.md) | 全 CLI の使い方 |
| [HISTORY.md](HISTORY.md) | 開発履歴・実測値 |
