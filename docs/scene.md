# Scene — 複数人物を「間」で合成する

## 何をするか

`bin/generate.py` は「1 キャラ × 1 台詞 → 1 WAV」。**scene** はそれを組み合わせ、
一つの場面を（シーンの余白＝間を含めて）**1 つの WAV** にする合成レイヤ。

- scene は voice の 7 段フロー（Validate→Route→Resolve→Generate→Normalize→Tag→Store）
  の**外側**に置く。各キューは既存の voice 生成そのもので作り、生成済み `Audio` を
  無音（間）で連結するだけ。voice の生成ループは変えない。
- scene は 5 Asset Type の正典に**加えない**（voice を組み合わせる「合成」であり、
  新たな asset_type ではない）。詳細は [asset-types.md](asset-types.md) Phase 4。

## scene.yaml（宣言的な源）

```yaml
name: gozen-niji-ch01
default_pause: 0.5          # 各キューの既定の間（秒）
cues:
  - character: gozen-niji-katari   # 語り（characters/<name>.voice.yaml をファイル名で参照）
    line: 夜の十一時。真白は、布団の中で、スマホをいじっていた。
    emotion: calm
    intensity: subtle
    volume: quiet
    speed: natural
    delivery: controlled
    subtext: 深夜の静けさ。
  - character: mashiro             # 真白
    line: ……まだ、起きてる？
    emotion: anxiety
    intensity: subtle
    volume: whisper
    subtext: 返事が怖い。
    pause_before: 0.8        # このキューの前だけ間を長く（default_pause を上書き）
```

`character` は表示名（語り・真白）ではなく `characters/<name>.voice.yaml` の
**ファイル名**（gozen-niji-katari・mashiro）で指定する（`bin/generate.py --character`
と同じ規約）。

各 cue の Direction（emotion / intensity / volume / speed / pitch / breathiness /
delivery）は `bin/generate.py` のフラグと同じ語彙。`line` はふりがな `漢字《かな》` と
キャラ名の自動ルビ（`name_reading`）に対応する。

## 間（余白）

「余白」＝**無音**。単位は秒。

- `pause_before` … そのキューの**前**に入れる無音。未指定（`None`）なら `default_pause` を継承。
- `default_pause` … シーンの既定の間（既定 0.0）。

間はタイムライン（mixer）の関心事なので、voice の `build_intent` には渡さない。
環境音・BGM の重ね合わせ、ducking・パン・クロスフェードは将来スコープ（Phase 4 の残り）。

## CLI

```bash
# 生成（scene.yaml → scene.wav + scene.params.yaml）
bin/scene.py --scene-file examples/works/gozen-niji-ch01/scene.yaml --project gozen-niji

# 再生成（保存済み Spec を再利用・LLM は呼ばない＝seed決定論）
bin/scene.py --params examples/works/gozen-niji-ch01/gozen-niji-ch01.params.yaml --out-dir /tmp/regen
```

- `--scene-file`（render）と `--params`（regen）は排他。片方必須。
- render の出力先は `projects/<project>/assets/<scene-name>/`。`scene-name` は
  `--name` > `scene.yaml` の `name` > ファイル名の順に決まる。
- seed 未指定のキューは render 時に採番し、`scene.params.yaml` の `parameters.cues`
  に記録する（voice の params.yaml と同じ再現性）。regen はこの保存済み Spec から
  各キューを `generate_request`（LLM なし）で再生成し、同じ間で連結する。

## 再現性

scene.params.yaml は各キューの resolved Spec（voice_profile / performance_spec /
dialogue / reading / seed）＋ `pause_before` を自己完結で保持する。同じ seed で
byte-identical に再生成できる（voice と同じ再現性の保証）。
