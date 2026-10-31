# Semantic Audio Loom

<p align="center">
  <img src="assets/repo-hero.png" width="100%" alt="semantic-audio-loom">
</p>

Context + Intent + State + Emotion + Performance Direction → 意味的音響アセット。

音を単なるファイルではなく、意味・文脈・感情を持った生成・再利用可能な音響アセットとして
扱うエンジン。正典は 5 種（voice / bgm / ambience / sfx / foley）で、すべて生成経路が動く。

設計の分かれ目は **Direction（監督＝意図）と Interpretation（俳優＝実現）の分離** と、
その境界に置くモデル非依存の **Spec**（voice = Performance Spec / bgm = Music Spec /
ambience・sfx・foley = Sound Spec）。声では台詞の「裏の意味（subtext）」を Spec へ解決して
渡すのが、テキスト読み上げとの差。音の 3 種では抽象語を「何が・どこで・どの材質で鳴るか」へ
具体化するのが、プロンプト直書きとの差。

⚠️ subtext が声を動かすのは、いまは**解決が触った強度の段**まで。抑揚の語
（flat / falling / wavering）は散文を変えても声を変えない（+1.0 Hz・2/5）。
`--resolve rule` では subtext は散文に載らない。測った中身は
[docs/resolve.md](docs/resolve.md)「どこまで声に届くか」。
台詞の文末の記号は、欄より強く声を動かす（`？` f0 +16.3 Hz・`！` +39.3 Hz・感情と
足し算。効きは行の形で縮む——途中に句点が 1 つあると 9 文字でも +14.6 Hz）。
詳細は `projects/longform/REPORT.md`。

## 資材の分離（再利用の設計）

再利用するもの（参照音声・キャラ・演技）と、使い捨てるもの（生成音声）を分ける。

| 資材 | ツール | 場所 |
| --- | --- | --- |
| 参照音声（声の実体） | `bin/reference.py` | `references/` |
| キャラ（誰の声か） | `bin/character.py` | `characters/<name>.voice.yaml` |
| 演技の振り付け（どう演じるか） | `bin/performance.py` | `performances/<name>.direction.yaml` |
| 生成音声（産物） | `bin/generate.py` | `projects/<project>/assets/<scene>/` |
| 音の生成（bgm/ambience/sfx/foley） | `bin/asset.py` | `projects/<project>/assets/<scene>/` |
| 音響ライブラリ（再利用する音） | `bin/library.py` | `library/<type>/<name>.asset.yaml` |
| 作品の音響スタイル | `bin/sound-bible.py` | `projects/<project>/sound-bible.yaml` |
| 場面（複数人物を間で合成） | `bin/scene.py` | `scene.yaml` → `projects/<project>/assets/<scene>/` |
| 統合（声・bgm・sfx を重ねる） | `bin/mix.py` | `mix.yaml` → 1 本の WAV |
| 生成物を測る（耳の代わり） | `bin/probe.py` | —（形式・帯域・無音率・先頭の段差） |

キャラと演技は独立に再利用でき、名前で組み合わせられる。生成音声はキャラ/演技資材と
混ぜず、プロジェクトごとに分離する。何度も使う音はライブラリへ移す。

## 状態

M0（Provider 確定）〜 M4（蒸留）、M5（音の生成＋ライブラリ）まで完了。履歴・実測値は
[HISTORY.md](HISTORY.md)。

## Asset Type

正典 5 種（**voice / bgm / ambience / sfx / foley**）。すべて生成経路が動く。
詳細とロードマップは [docs/asset-types.md](docs/asset-types.md)、音の作り方は
[docs/asset-generation.md](docs/asset-generation.md)。

## クイックスタート

```bash
pip install -r requirements.txt          # 依存（コアのみ。生成は別途 Tsukasa が要る）

bin/reference.py list                    # 登録済み参照音声
bin/character.py list                    # 登録済みキャラ
bin/performance.py list                  # 登録済み演技

bin/generate.py --character mashiro --performance anxious-night-call \
    --project demo --scene night \
    --line "……まだ、起きてる？" --name mashiro_night

bin/asset.py --type bgm --project demo --name lonely-room \
    --sound role=underscore --sound mood=lonely --duration 20   # 音の生成
bin/library.py list                                              # 再利用ライブラリ
bin/probe.py projects/demo/assets/sound/lonely-room.wav           # できた音を測る
```

セットアップの詳細（Tsukasa・音生成モデル・LLM の設定）は [docs/setup.md](docs/setup.md)、
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

核心は **Resolve**（Direction → Spec）。asset_type ごとに Spec が変わるが、7 段の骨格は
共通。声の Resolve は [docs/resolve.md](docs/resolve.md)、音の Resolve は
[docs/asset-generation.md](docs/asset-generation.md)。

## 構成

```
characters/  performances/  references/   # 再利用資材（キャラ・演技・参照音声）
library/                                   # 再利用する音響資材（生成物ではない）
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
| [docs/asset-generation.md](docs/asset-generation.md) | 音の生成（bgm/ambience/sfx/foley・Provider） |
| [docs/library.md](docs/library.md) | 再利用ライブラリ（意味タグ・出典・検索） |
| [docs/sound-bible.md](docs/sound-bible.md) | Sound Bible（作品の音響スタイル） |
| [docs/distill.md](docs/distill.md) | 蒸留（大量インプット → キャラ/演技） |
| [docs/loudness.md](docs/loudness.md) | 声量の三層分業 |
| [docs/scene.md](docs/scene.md) | シーン合成（複数人物×間） |
| [docs/reference-voices.md](docs/reference-voices.md) | 参照音声と拡充・弱い声への方針 |
| [docs/setup.md](docs/setup.md) | セットアップ（Tsukasa・LLM・環境変数） |
| [docs/usage.md](docs/usage.md) | 全 CLI の使い方 |
| [projects/longform/README.md](projects/longform/README.md) | 長尺（5〜10 分）の組み方：間・音量・効果音・ducking |
| [projects/longform/INDEX.md](projects/longform/INDEX.md) | 長尺の索引：ディレクトリの地図・走らせ方・数字の読み方 |
| [HISTORY.md](HISTORY.md) | 開発履歴・実測値 |
