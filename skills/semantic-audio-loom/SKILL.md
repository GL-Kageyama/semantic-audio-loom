---
name: semantic-audio-loom
description: Semantic Audio Loom の音声素材エンジン。Context + Intent + State + Emotion + Performance Direction から、台詞の裏の意味（subtext）まで反映した音声を生成する。参照音声（声の実体）→ キャラ（誰の声か）→ 演技（どう演じるか）の 3 資材を名前で再利用して、台詞ごとに演技付きの声を生成する。
argument-hint: '(optional) キャラ名・演技名・台詞。例: /semantic-audio-loom キャラ mashiro・演技 anxious-night-call・台詞「……まだ、起きてる？」'
---

# semantic-audio-loom — 意味的音声アセット生成

台詞の「裏の意味（subtext）」まで反映した音声を生成するエンジン。設計の分かれ目は **Direction（監督＝意図）と Interpretation（俳優＝実現）の分離**。

## 資材モデル（再利用するもの / 使い捨てるもの）

| 資材 | 役割 | ツール | 場所 |
| --- | --- | --- | --- |
| 参照音声 | 声の実体 | `bin/reference.py` | `references/` |
| キャラ | 誰の声か | `bin/character.py` | `characters/*.voice.yaml` |
| 演技の振り付け | どう演じるか | `bin/performance.py` | `performances/*.direction.yaml` |
| 生成音声 | 産物（使い捨て） | `bin/generate.py` | `projects/*/assets/` |

## ワークフロー

1. **参照音声が足りていれば確認** — `bin/reference.py list`。足りない声は `synthesize <key> --character <name>`（ローカル生成）か `add <wav> <key> --license …`（著作権フリー音源）で拡充。
2. **キャラを作る**（誰の声か）— `bin/character.py init <name>` → `characters/<name>.voice.yaml` を編集（`reference_audio` で参照音声を指定）。
3. **演技を定義する**（どう演じるか）— `bin/performance.py init <name>` → `performances/<name>.direction.yaml` を編集（emotion / intensity / volume / speed / delivery / situation / subtext）。
4. **声を生成する** — `bin/generate.py --character <キャラ> --performance <演技> --line <台詞>`。

## 声の生成

```bash
bin/generate.py --character mashiro --performance anxious-night-call \
    --project demo --scene night \
    --line "……まだ、起きてる？" --name mashiro_night
```

- キャラ（誰）と演技（どう演じる）は独立に再利用できる。同じキャラで別の演技、別のキャラで同じ演技。
- 演技資材は CLI フラグで上書きできる（`--emotion joy` など未指定分は資材の値を引き継ぐ）。
- `--resolve llm`（既定）で subtext を具体的な抑揚（語尾 intonation）へ変換。`--resolve rule` は決定的写像（LLM なし）。
- 台詞は日本語。`--seed` で再現可能。

## 実行環境

- 生成実行には Tsukasa_Speech（~5GB）と `SAL_TSUKASA_DIR` の指定が必要。詳細は README のセットアップ。
- 参照音声の欠落は generate.py が既定で検知し、拡充コマンドを案内する。

## 深掘り

- `docs/resolve.md` — subtext を音に乗せる Resolve（M2 の核心）
- `docs/loudness.md` — 声量の三層分業
- `docs/reference-voices.md` — 参照音声と拡充
