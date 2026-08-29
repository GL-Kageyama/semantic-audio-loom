# Asset Type — 正典 5 種とロードマップ

音を「声」に閉じない。このエンジンは構想段階から、声・音楽・環境音・効果音を
別々の再利用可能な Asset として扱う。ここに正典 5 種と実装状態を残す。

## 5 Asset Type（正典）

| Asset Type | 内容 | 例 |
| --- | --- | --- |
| **voice** | キャラ・ナレーターの発話 | 台詞・独白・ナレーション・囁き・感情・呼吸・笑い・泣き |
| **bgm** | 感情・空気を支える音楽 | bgm / theme / jingle |
| **ambience** | 空間・時間・環境を表現する音 | 雨・風・夜・部屋・街・駅・学校・森・海・虫・機械音 |
| **sfx** | 出来事・操作・物体の音 | phone / door / notification / footstep |
| **foley** | 映像内の身体・物体の細かな動き | breathing / clothes / futon / paper |

正典の実体は `semantic_audio_loom/types.py` の `ASSET_TYPES` と
`schemas/asset_type.schema.json`（enum）。`validate_intent` は enum 外の
asset_type を拒否する。

## 実装状態

**実装済みは `voice` のみ**（Phase 1 Character Voice）。残り 4 種は将来スコープで、
現時点では生成モデル・Resolve 経路・Sound Bible とも未実装。

| Phase | 内容 | 状態 |
| --- | --- | --- |
| 1 — Character Voice | voice / WAV / Metadata | 実装済み |
| 2 — Ambience / SFX | ambience・sfx Skill → Local Audio Models | 将来 |
| 3 — BGM | bgm Skill → Local / Cloud Music Model | 将来 |
| 4 — Audio Mixing | 音量・タイミング・フェード・パン・ducking・マスター | 将来 |
| 5 — Video Integration | 映像と音響を Scene Definition から分岐 | 将来 |

## なぜ正典化するか

Phase 1 は声に閉じているが、設計の骨格（7 段フロー・Provider 契約・AudioAsset）は
asset type 非依存。5 種を「正典」として明文化しておくことで、将来 ambience/sfx/bgm
を追加する際に「何を足すべきか」が自明になる：

- **Asset Type 別の意味フィールド**（ambience の environment/weather/time/mood、
  sfx の event/object、bgm の music_style/tempo/mood）を GenerationIntent に足す
- **Resolve の別経路**（声は「抑揚指示」へ、環境音・効果音・BGM は「意味記述 → 生成
  プロンプト／パラメータ」へ）
- **Sound Bible**（作品全体の音響スタイル。music/ambience/sfx/dialogue の style を
  定義する層。現 repo には未実装）

これらは今回スコープ外（実装しない）。将来スコープを閉じないための最小のしるし。
