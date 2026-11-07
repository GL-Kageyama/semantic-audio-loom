# gozen-niji-ch01 — 真白・ニジ・語りを 1 場面に合成する例

`scene.yaml` が 3 声（語り／真白／ニジ）のキューと「間（余白）」を宣言し、
`bin/scene.py` が各キューを voice 生成してから無音で連結し、1 つの WAV にする。

このディレクトリに**生成済みの成果物**（`gozen-niji-ch01.wav` と
`gozen-niji-ch01.params.yaml`）も置いてある。

## 生成（再実行）

```bash
bin/scene.py --scene-file examples/gozen-niji-ch01/scene.yaml --project gozen-niji
```

出力: `projects/gozen-niji/assets/gozen-niji-ch01/gozen-niji-ch01.wav` と
`gozen-niji-ch01.params.yaml`（各キューの resolved Spec＋間を保持）。

## 再生成（LLM なし・byte-identical）

```bash
bin/scene.py --params examples/gozen-niji-ch01/gozen-niji-ch01.params.yaml \
    --out-dir /tmp/gozen-niji-ch01-regen
```

同じ seed から byte-identical に再生成される（seed決定論）。

## キューの内訳

| 順 | character（ファイル名） | 表示名 | 台詞 | pause_before |
| --- | --- | --- | --- | --- |
| 1 | gozen-niji-katari | 語り | 夜の十一時。真白は… | （default_pause） |
| 2 | mashiro | 真白 | ……まだ、起きてる？ | 0.8 秒 |
| 3 | niji | ニジ | 起きてるよ。ずっと、待ってた。 | （default_pause） |

`default_pause: 0.6` が各キューの既定の間（秒）。`pause_before` は個別上書き。

詳細は [docs/scene.md](../../docs/scene.md)。
