# 使い方 — 全 CLI

## 参照音声の拡充（bin/reference.py）

```bash
bin/reference.py list                                    # 登録済み参照音声一覧
bin/reference.py synthesize elderly_man --character mashiro   # ローカル生成（経路B・参照不要）
bin/reference.py add my_voice.wav old_woman --gender F --age sixties \
    --license "CC0" --source "Common Voice"               # 著作権フリー音源を登録
```

経路B（ローカル生成）は女性バイアスが強い。男性・老人の確実な声は `add`（著作権フリー
音源の登録）が向く。詳細は [reference-voices.md](reference-voices.md)。

## キャラ作り（bin/character.py）

```bash
bin/character.py init mashiro            # characters/mashiro.voice.yaml を生成
bin/character.py validate mashiro        # スキーマ検証
bin/character.py list                    # 登録済みキャラ一覧
```

## 演技の振り付け（bin/performance.py）

```bash
bin/performance.py init anxious-night-call
bin/performance.py validate anxious-night-call
bin/performance.py list
```

## 声の生成（bin/generate.py）

```bash
bin/generate.py --character mashiro --performance anxious-night-call \
    --project demo --scene night \
    --line "……まだ、起きてる？" --name mashiro_night
```

- キャラ + 演技を名前で再利用。未指定の演技フラグは資材値を引き継ぐ。
- `--emotion joy` など CLI フラグで演技資材を上書きも可。
- `--resolve llm`（既定）で Resolve を LLM に、`--resolve rule` で決定的写像（API なし）。
- `--situation` と `--state-file`（character_state の YAML）が subtext 推論の入力。
  `--subtext` で人間が裏の意味を直接指定もできる。
- 台詞は日本語（Tsukasa は `phonemize` で読みへ変換）。`--seed` で再現可能。
- 漢字の読みが誤読される語（例: `既読`→`きよみ`）は、`--line` 内でふりがなを指定できる。
  `漢字《かな》` の記法で、`《》` は読みにだけ使われ、保存される台詞からは外れる。

  ```bash
  --line "既読《きどく》を付けて、画面を閉じる。"   # 「きどく」と発音
  ```

- キャラ名（固有名詞）は `characters/*.voice.yaml` の `name_reading` に読みを書いておくと、
  台詞中のその名前へ自動でふりがなが振られる（`《》` を手で書かなくてよい）。語り（ナレーション）
  などで話者が本人でない場合に有効。例: 真白（`name_reading: ましろ`）→「真白は」が「ましろは」
  と発音される。手書き `《》` と自動ふりがなは共存でき、両方とも読みへ反映される。

## 音の生成（bin/asset.py）

bgm / ambience / sfx / foley を声と同じ 7 段フローで作る。

```bash
bin/asset.py --type bgm --project demo --name lonely-room \
    --sound role=underscore --sound mood=lonely --sound instrumentation=solo_piano \
    --duration 20                                  # 既定 Resolve=llm

bin/asset.py --type sfx --project demo --name door-close \
    --sound event="heavy wooden door closing" --duration 3 \
    --resolve rule --provider stub                  # 依存なしで配線を確認

bin/asset.py --type ambience --sound-file rain.yaml --duration 30 \
    --save-library steady-rain --tags rain,night    # ライブラリへも取り込む
```

- Direction は `--sound key=value`（複数可）。カンマ区切りは配列、`{...}` は JSON。
- `--duration` / `--prompt` / `--situation` / `--subtext` / `--seed` / `--provider`。
- `--bible` を省略すると `projects/<project>/sound-bible.yaml` を自動で読む（`--no-bible` で無効）。
- プロンプトは英語（モデル向け）。詳細は [asset-generation.md](asset-generation.md)。

## ライブラリ（bin/library.py）

```bash
bin/library.py list [--type sfx]
bin/library.py search "rain night" [--type ambience]
bin/library.py show door-close
bin/library.py add my_rain.wav --type ambience --name steady-rain --tags rain
bin/library.py validate
```

詳細は [library.md](library.md)。

## Sound Bible（bin/sound-bible.py）

```bash
bin/sound-bible.py init demo       # projects/demo/sound-bible.yaml
bin/sound-bible.py show demo
bin/sound-bible.py validate demo
```

詳細は [sound-bible.md](sound-bible.md)。

## シーン合成（bin/scene.py）

複数人物の台詞を「間（無音）」で連結し、1 つの WAV にする。`scene.yaml` がキュー
（キャラ＋台詞＋Direction＋`pause_before`）を宣言し、各キューを voice 生成で作ってから連結する。

```bash
# 生成（scene.yaml → scene.wav + scene.params.yaml）
bin/scene.py --scene-file examples/gozen-niji-ch01/scene.yaml --project gozen-niji

# 再生成（保存済み Spec を再利用・LLM なし＝seed決定論）
bin/scene.py --params examples/gozen-niji-ch01/gozen-niji-ch01.params.yaml --out-dir /tmp/regen
```

- `--scene-file`（render）と `--params`（regen）は排他。片方必須。
- 間（余白）＝無音。`default_pause`（秒）が各キューの既定、`pause_before`（秒）で個別上書き。
- 環境音・BGM・ducking・パンは将来スコープ。詳細は [scene.md](scene.md)。

## 再生成（bin/regenerate.py）

保存済み Spec を再利用・LLM は呼ばない（再現性）。

```bash
bin/regenerate.py examples/mashiro-night/mashiro_night.params.yaml \
    --out-dir /tmp/regen
```

## 蒸留（bin/distill.py）

手で埋める `init` の代わりに、物語・脚本・人物描写からキャラと演技を自動生成する：

```bash
bin/distill.py batch story.txt                    # 一括蒸留：物語 → 主要キャラ複数 × 代表シーン複数
bin/distill.py character "金髪で低い声の青年" --name rei      # 単発：キャラ1体
bin/distill.py performance "深夜、返事が怖い電話" --name anxious-call  # 単発：演技1つ
```

`--synthesize` でキャラの元音声（経路B）も生成・登録、`--dry-run` で書き出さず YAML を確認。
設計（理解→選択→翻訳・schema 制約）は [distill.md](distill.md)。
