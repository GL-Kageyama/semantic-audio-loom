# ライブラリ — 再利用する音響資材

生成物（`projects/*/assets/`）は使い捨て。何度も使う音は `library/` へ移し、
意味タグと出典を持たせて再利用する。キャラ（`characters/`）・演技（`performances/`）・
参照音声（`references/`）と同じ「再利用する資材」の側にある。

## 置き場

```
library/
  bgm/       lonely-room.asset.yaml + lonely-room.wav
  ambience/  station-night.asset.yaml + station-night.wav
  sfx/       door-close.asset.yaml + door-close.wav
  foley/     cloth-rustle.asset.yaml + cloth-rustle.wav
```

置き場は `SAL_LIBRARY_DIR` で変えられる（既定はリポジトリ直下 `library/`）。
1 資材の正典は `<name>.asset.yaml`（`schemas/library_asset.schema.json`）。

| フィールド | 内容 |
| --- | --- |
| `name` / `asset_type` | 識別 |
| `spec` | Resolve 済みの Spec（プロンプトを含む） |
| `semantic` | 検索用の意味フィールド（environment / event / mood / tempo …） |
| `tags` | 自由なタグ |
| `loop` | ループ点（enabled / start / end / crossfade） |
| `license` / `attribution` | 配布に必要な表示 |
| `source` | provider / seed / prompt（再現の手がかり） |
| `files.wav` / `duration` / `sample_rate` / `channels` | 実体 |

## 取り込む

```bash
# 生成と同時にライブラリへ
bin/asset.py --type sfx --project demo --name door-close \
    --sound event="heavy wooden door closing" --duration 3 \
    --save-library door-close --tags door,wood --license "generated"

# 手元の WAV を登録
bin/library.py add my_rain.wav --type ambience --name steady-rain \
    --tags rain,night --semantic environment=rain --license "CC0" \
    --attribution "recorded by ..."
```

`add` は WAV のサンプルレート・チャンネル・長さを実測して書き込む。

## 探す

```bash
bin/library.py list                  # 全部
bin/library.py list --type sfx       # 型で絞る
bin/library.py search "rain night"   # 意味フィールド・タグ・プロンプトの部分一致
bin/library.py search wood --tags door
bin/library.py show door-close       # YAML で表示
bin/library.py validate              # 全件検証（メタデータ + WAV の存在）
```

検索は埋め込みではなく、語の部分一致を数えて順位を付ける決定的な方式。
意味フィールド・タグ・Spec のプロンプトを対象にする。該当ゼロはゼロとして返す。

## ライセンス

`license` と `attribution` は空でも保存できるが、配布するなら必ず埋める。
`source.provider` が `stub` の資材は本物の音ではないので配布しない。
