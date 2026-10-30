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

5 種すべてに生成経路がある。voice は Performance Spec、bgm は Music Spec、
ambience/sfx/foley は Sound Spec を Resolve が作り、7 段フローを通る。

| Phase | 内容 | 状態 |
| --- | --- | --- |
| 1 — Character Voice | voice / WAV / Metadata | 実装済み |
| 2 — Ambience / SFX | ambience・sfx Skill → Local Audio Models | 実装済み（Stable Audio Open） |
| 3 — BGM | bgm Skill → Local Music Model | 実装済み（MusicGen small） |
| 4 — Audio Mixing | 音量・タイミング・フェード・パン・ducking・マスター | 一部実装済み（voice 連結のみ） |
| 5 — Video Integration | 映像と音響を Scene Definition から分岐 | 将来 |

Phase 4 のうち **voice 合成（Scene / Timeline）** は実装済み：複数 voice キューを無音
（間）で連結して 1 WAV にする（`bin/scene.py`・[scene.md](scene.md)）。ducking・パン・
クロスフェード・LUFS マスター正規化、および ambience/bgm の重ね合わせは将来スコープ。

音の生成とライブラリは [asset-generation.md](asset-generation.md)・[library.md](library.md)。
Sound Bible は [sound-bible.md](sound-bible.md)。

## なぜ正典化するか

設計の骨格（7 段フロー・Provider 契約・AudioAsset）は asset type 非依存。正典を先に
決めておいたことで、追加時に「何を足すべきか」が自明だった：

- **Asset Type 別の意味フィールド**（ambience の environment/weather/time/mood、
  sfx の event/object、bgm の genre/tempo/instrumentation）→ `GenerationIntent.sound`
- **Resolve の別経路**（声は「抑揚指示」へ、環境音・効果音・BGM は「意味記述 → 生成
  プロンプト／パラメータ」へ）→ `resolve_music_*` / `resolve_sound_*`
- **Sound Bible**（作品全体の音響スタイル）→ `projects/<project>/sound-bible.yaml`

いま残っているのはミキサー（M6・複数トラックの重ね合わせ・ducking・LUFS）と、
脚本から音の設計図を起こす段（M7）。
