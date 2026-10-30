# Sound Bible — 作品の音響スタイル

作品全体で音の質感を揃えるための辞書。Direction が個々の音を決め、Sound Bible が
その既定（style / palette / negative）を供給する。置き場は
`projects/<project>/sound-bible.yaml`（正典は `schemas/sound_bible.schema.json`）。

## 作る・見る・検証する

```bash
bin/sound-bible.py init demo       # テンプレートを書く
bin/sound-bible.py show demo
bin/sound-bible.py validate demo
```

## 形

```yaml
project: demo
notes: ""

music:
  style: [lofi, intimate]
  instrumentation: [felt piano, tape hiss]
  negative: [drums, EDM drop]

ambience:
  style: [field recording]
  palette: [rain, room tone]
  negative: [traffic]

sfx:
  style: [organic, close-mic]
  palette: [wood, cloth]
  negative: [cartoon]

foley:
  style: [naturalistic]
  palette: [futon, paper]
  negative: [exaggerated]

dialogue:
  style: [close, naturalistic]
  negative: [announcer]
```

## 効き方

`bin/asset.py` は `--bible` か `projects/<project>/sound-bible.yaml` があれば自動で読み、
Direction の**未指定フィールドだけ**を補う。

- `style` / `instrumentation` / `palette` は Direction が優先（作品の既定より個別指定が強い）。
- `negative` は Direction の `negative` に追記する。
- `--no-bible` で読まない。

`loudness`（`target_lufs` / `true_peak_db`）はスキーマにあるが、**まだ適用していない**。
ラウドネス正規化はミキサー（M6）で入れる。`dialogue` は voice の Resolve へまだ繋いでいない。
