# HISTORY — 開発履歴

日付入りの変更経緯・過去の設計との比較・実測値はここに記録する。現在の情報は README / docs / SKILL を見る。

## 2026-10-31 — M5 音の生成＋ライブラリ（5 種すべて）

### スコープ

- 正典 5 種のうち voice しか動いていなかった状態から、bgm / ambience / sfx / foley を
  同じ 7 段フローに乗せた。資材の範囲は 5 種すべて、生成はローカル優先（クラウドは任意）、
  最初の縦の一本は「生成＋ライブラリ」（ユーザー選択）。
- Scene（複数 voice の連結）は正典 5 種に数えないまま。Timeline / Mixer（重ね合わせ・
  ducking・LUFS）は M6、脚本→音の設計図は M7。

### 設計

- Seam（モデル非依存の境界）を type 別の Spec に一般化：voice=Performance Spec、
  bgm=Music Spec、ambience・sfx・foley=Sound Spec。`GenerationRequest` は
  `performance_spec` をやめて `spec` ＋ `asset_type` を持つ（`performance_spec` は
  後方互換の property として残す）。
- `GenerationIntent.sound`（dict）を追加。voice の Direction フィールドはそのまま。
- Resolve は type で分岐。Rule は構造フィールドを Spec へ移し、英語プロンプトを組み立てる。
  LLM は 3 つのプロンプト（resolve / resolve_music / resolve_sound）を使い分ける。
- Route は asset_type ごとの既定 Provider を持ち、`capabilities()["asset_types"]` で
  非対応を即座に落とす（生成してから気づかない）。
- 保存形式は type 別（`config.OUTPUT_FORMATS`）。voice は従来どおり 24kHz mono、
  音の 4 種は 44.1kHz・チャンネルは生成のまま。Normalize にリサンプルとチャンネル変換を
  足し、ループ資材には末尾フェードを掛けない。
- 新規スキーマ：`music_spec` / `sound_spec` / `sound_bible` / `library_asset`。
- 新規 Provider：`musicgen`（transformers・musicgen-small・32kHz mono・30 秒）、
  `stable_audio`（diffusers・stable-audio-open-1.0・44.1kHz stereo・約 47 秒・gated）、
  `stub`（依存なし・決定的）。
- 新規 CLI：`bin/asset.py`（音の生成）、`bin/library.py`（一覧・検索・追加・検証）、
  `bin/sound-bible.py`（init/show/validate）。
- ライブラリは `library/<type>/<name>.asset.yaml` ＋ `.wav`。検索は埋め込みでなく
  意味フィールド・タグ・プロンプトの部分一致を数える決定的な方式。
- `projects/` の解決を `config.project_dir()` に一本化（`SAL_PROJECTS_DIR` で差し替え可）。

### 検証

- `pytest tests/` … 85 passed（既存 55 ＋ 新規 30）。重いモデルは使わず stub で全 type の
  7 段フロー・保存形式（チャンネル／サンプルレート）・ライブラリの追加と検索・Sound Bible の
  継承規則・Route の非対応拒否を通した。i18n は `resolve_music` / `resolve_sound` の
  プロンプトが `--lang` で切り替わること（かな漏れ無し）をモック LLM で確認した。
- CLI 実測（stub）：`sound-bible init → asset(bgm/ambience) → library list/search/validate
  → regenerate` が通り、regenerate は同じ seed で走った。
- **musicgen は本物の重みで通した**（`facebook/musicgen-small`・CPU・M2 Pro）。3 秒と 5 秒の
  BGM を生成 → リサンプル（32kHz → 44.1kHz）→ 保存まで通り、wav は peak 0.95・RMS 0.176
  （−15 dBFS）・無音率 0.08%・末尾フェードあり。所要は 5 秒の BGM で約 37 秒（重み取得済み）。
  初回は重み 2.2GB の取得を含めて約 2 分。
- **stable_audio は未実測**。モデルが gated で、この環境には diffusers も HF のトークンも
  無い。ライセンス同意と `huggingface-cli login` のあとで `--provider stable_audio` を
  通すのが次の実測。ambience / sfx / foley の保存形式は stub でのみ確認している。
- 空の検査を「健全」と言わないよう直した：ライブラリ 0 件の `library.py validate` と、
  全節が空の Sound Bible の `validate` は、OK でなく「空」と報せる。

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

## 2026-08-30 — 読み（ふりがな）の指定（漢字の誤読対策）

- 実測：Tsukasa の phonemize（cutlet / UniDic）が「既読」を `kijomi`（きよみ）と誤読する。
  `phonemize('既読') => kijomi`、かな読み `phonemize('きどく') => kidokɯ` は正しい。
  つまり、かなを渡せば正しく発音される（漢字→かな変換だけが誤読の原因）。
- 対処：`--line` 内に `漢字《かな》` のふりがなを指定できるようにした。`parse_ruby`
  （`semantic_audio_loom/text.py`）が台詞を（表示用台詞, 読み）に分解し、プロバイダは
  `reading` があればそれを phonemize、無ければ台詞をそのまま phonemize（従来どおり）。
  保存される台詞（dialogue）は `《》` を外した綺麗な文。`reading` は params.yaml に保存し
  regenerate が再現する。
- 入力 UI はふりがな《》記法のみ（`--reading` フラグは追加しない、ユーザー確認済み）。
  未アノテーションの漢字は従来どおり cutlet が読む。
- 新設: `semantic_audio_loom/text.py`（parse_ruby）、`tests/test_text.py`（4件）。

## 2026-08-30 — キャラ名の自動ふりがな（name_reading）

- 実測：語りサンプルで「真白」が `maʔɕiɽo`（まっしろ＝普通名詞「真っ白」）と誤読された。
  固有名詞の誤読は手書き《》で都度直すには漏れやすく、特にナレーション（話者＝語り）では
  本人でないキャラ名が台詞に頻出する。
- 対処：`characters/*.voice.yaml` に `name_reading`（キャラ表示名の読み）を追加。`build_intent`
  が全キャラの `name_reading` をレジストリ化し、台詞中のキャラ名へ `annotate_reading`
  （`text.py`、既アノテーションをスキップして `漢字《かな》` を挿入）で自動ルビを振る。
  手書き《》と自動ふりがなは共存し、両方とも `reading` へ反映される。
- `mashiro.voice.yaml` に `name_reading: ましろ` を追加（真白→まっしろ誤読への対処）。
  語りサンプル（opening / refrain / ending）を再生成し、`reading` に「ましろ」が入ることを
  params.yaml で確認。
- 新設: `text.py` に `annotate_reading`、`tests/test_text.py`（+3件）、`tests/test_character_voice.py`（3件）。

## 2026-08-30 — Scene / Timeline（複数人物 × 間の合成）

- 動機：`bin/generate.py` が「1 キャラ × 1 台詞 → 1 WAV」に閉じ、真白・ニジ・語りを
  「一つの場面（余白含む）として 1 WAV に複数人物を登場させる」ことができなかった。
  外部 DAW 合成だと間のタイミングが DAW プロジェクトに閉じ、seed決定論（再生）が壊れる。
- 設計：scene は voice の 7 段フローの外側に置く合成レイヤ。`scene.yaml`（宣言的な源）が
  キュー（キャラ＋台詞＋Direction＋pause_before）を宣言し、各キューを既存 voice 生成で
  作って無音（間）で連結する。scene は 5 Asset Type の正典に加えない（voice の合成）。
- 「間（余白）」＝無音（秒）。`pause_before`（個別）と `default_pause`（既定）。既存
  `performance_direction.schema.json` に予約済みだった `pause_before` の語彙を採用。
- 再現性：render が seed を採番して `scene.params.yaml` の `parameters.cues` に各キュー
  の resolved Spec（voice_profile / performance_spec / dialogue / reading / seed）＋
  pause_before を記録。`bin/scene.py --params` が `generate_request`（LLM なし）で
  byte-identical に再生成。
- 環境音・BGM・ducking・パン・クロスフェード・LUFS マスターは将来スコープ（Phase 4 の残り）。
- 新設: `engine/mix.py`（silence/mix_cues）、`scene.py`（load_scene/cue_from_params）、
  `schemas/scene.schema.json`、`bin/scene.py`、`tests/test_mix.py`（6件）、`tests/test_scene.py`（7件）。
  `types.py` に SceneCue/Scene、`engine/validate.py` に validate_scene、locales ×3 に scene。

## 2026-08-30 — 省略記号「…」が「へぇ」に化ける問題の対処

- 実測：scene 例の真白の台詞「……まだ、起きてる？」が「へぇ…まだ、起きてる？」と聞こえる。
  原因は Tsukasa の phonemize（cutlet）が「…」をドット列に変え（`……まだ` → `...... mada`）、
  モデルがそのドット列を有声（「へぇ」様）に読み上げること。構造化ポーズ（間）は非対応。
- 対処：`text.py` に `normalize_ellipsis` を追加し、phonemize の**入力だけ**を正規化する。
  文頭・文末の「…」は除去（間は scene の `pause_before` や emotion/delivery が担う）、
  文中の「…」は「、」に置換（ポーズ境界）。台詞（dialogue）自体は変えない＝表示・
  params.yaml は従来どおりで、seed決定論（再生成）も保たれる。
- 適用先は `providers/tsukasa.py` の `generate`（`request.reading or dialogue` を
  正規化してから phonemize）。`tests/test_text.py` に +5 件。
