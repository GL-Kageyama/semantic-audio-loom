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
