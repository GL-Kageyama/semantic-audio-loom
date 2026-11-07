# examples/

生成の見本と、聞き比べ用の音を置く。

## 配置

```
examples/
├── works/          作品・場面のまとまり（1作品＝1フォルダ）
│   ├── gozen-niji-ch01/
│   ├── gozen-niji-katari-scenes/
│   ├── mashiro-night/
│   ├── mashiro-scenes/
│   ├── niji-scenes/
│   └── mixed-scene/
├── longform/       ノブごとの聞き比べ（1実験＝1フォルダ）
├── sound-samples/  単発の音素材（ambience / bgm / foley / sfx）
├── _archive/       一度きりの出力・旧版
└── README.md
```

## 置き方の指針

新しい見本は、次の順で置き場所を決める。

1. **特定の作品・場面に属するか** → `works/<作品名>/`
2. **ノブ（演技・間・強弱など）の聞き比べか** → `longform/<実験名>/`
3. **単発の音素材か** → `sound-samples/`
4. **一度きりの出力・旧版・backup か** → `_archive/`

- 直下に音を置かない。必ず分類フォルダの下に置く。
- 1見本1フォルダ。`params.yaml` と `wav` を同じフォルダに置く。
- 名前は kebab-case。作品名を先頭に付ける（`<work>_<scene>`）。
- 配布する MP3 と見本 WAV は Git LFS を通る。
- 追加したら上の配置図を更新する。
