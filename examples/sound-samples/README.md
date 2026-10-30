# 音の生成サンプル — bgm / ambience / sfx / foley

声の例は [../mashiro-night/](../mashiro-night/) にある。ここは残り 4 種。

| ファイル | type | Provider | 長さ | 形式 |
| --- | --- | --- | --- | --- |
| `bgm-lonely-room.wav` | bgm | musicgen（本物のモデル） | 9.94 秒 | 44.1kHz mono |
| `bgm-train-window.wav` | bgm | musicgen（本物のモデル） | 9.94 秒 | 44.1kHz mono |
| `sfx-door-slam.wav` | sfx | stable_audio（本物のモデル） | 2 秒 | 44.1kHz stereo |
| `sfx-glass-break.wav` | sfx | stable_audio | 2 秒 | 44.1kHz stereo |
| `sfx-gravel-steps.wav` | sfx | stable_audio | 4 秒 | 44.1kHz stereo |
| `sfx-thunder-far.wav` | sfx | stable_audio | 6 秒 | 44.1kHz stereo |
| `sfx-switch-click.wav` | sfx | stable_audio | 1 秒 | 44.1kHz stereo |
| `sfx-paper-tear.wav` | sfx | stable_audio | 2 秒 | 44.1kHz stereo |
| `ambience-station-night.wav` | ambience | stub | 6 秒 | 44.1kHz stereo |
| `sfx-door-close.wav` | sfx | stub | 2 秒 | 44.1kHz mono |
| `foley-cloth-rustle.wav` | foley | stub | 2 秒 | 44.1kHz mono |

`.params.yaml` は同じ名前で並べてある。Spec・seed・sha1・`provider_settings`
（サンプリング回数）が入っていて、`bin/regenerate.py` がこれを読んで同じ音を出し直す。

> **stub の 3 本は音楽でも効果音でもない。** 依存なしで 7 段フロー・保存形式・ライブラリを
> 通すための合成音（決定的なサイン波＋ノイズ）。本物の ambience / sfx / foley は
> `stable_audio`（gated）で出す。

## Direction → プロンプト → 音

`--resolve rule` は LLM を使わず、Direction の構造フィールドから英語のプロンプトを
組み立てる。何を書くと何になるかが、そのまま読める。

### bgm-lonely-room

```bash
bin/asset.py --type bgm --project demo --scene samples --name bgm-lonely-room \
    --resolve rule --provider musicgen --seed 42 \
    --sound role=underscore --sound mood=lonely,still \
    --sound instrumentation="felt piano" --sound tempo='{"bpm":60}' \
    --sound duration=10 --situation "深夜の一人暮らしの部屋。窓の外は雨。"
```

できたプロンプト:

```
An understated felt piano piece, lonely and still, slow. About 10 seconds.
```

楽器を主語にした一文にする（`60 BPM` や `no vocals` は音の説明でないので書かない。
理由は [../../docs/asset-generation.md](../../docs/asset-generation.md)）。
日本語の `situation` はプロンプトに入らない（生成モデルは英語で学習した T5 なので、
日本語は無意味なトークン列になる）。`subtext` として Spec と metadata に残る。

実測（`bin/probe.py`）：peak 0.95・RMS −18.5 dBFS・無音率 4.6%・帯域 低 −18.8 /
中 −0.1 / 高 −38.4 dB・重心 696 Hz。

### bgm-train-window

```bash
bin/asset.py --type bgm --project demo --scene samples --name bgm-train-window \
    --resolve rule --provider musicgen --seed 7 \
    --sound role=underscore --sound genre=folk --sound mood=wistful,gentle \
    --sound instrumentation="nylon guitar" --sound tempo='{"bpm":86}' \
    --sound duration=10 --situation "朝の各駅停車。窓の外を田んぼが流れる。"
```

できたプロンプト:

```
An understated nylon guitar piece, wistful and gentle, moderate tempo. About 10 seconds.
```

実測：peak 0.95・RMS −15.5 dBFS・無音率 2.6%・帯域 低 −7.4 / 中 −0.9 / 高 −41.9 dB・
重心 242 Hz。

### ambience-station-night（stub）

```bash
bin/asset.py --type ambience --project demo --scene samples --name ambience-station-night \
    --resolve rule --provider stub --seed 3 \
    --sound environment="empty train station at night" --sound space=indoor \
    --sound density=sparse --duration 6
```

```
empty train station at night, indoor space, sparse density, continuous ambience. About 6 seconds.
```

### sfx-door-close（stub）

```bash
bin/asset.py --type sfx --project demo --scene samples --name sfx-door-close \
    --resolve rule --provider stub --seed 11 \
    --sound event="heavy wooden door closing" --sound material=wood \
    --sound distance=near --duration 2
```

```
heavy wooden door closing, wood, near perspective, single sound effect. About 2 seconds.
```

### foley-cloth-rustle（stub）

```bash
bin/asset.py --type foley --project demo --scene samples --name foley-cloth-rustle \
    --resolve rule --provider stub --seed 5 \
    --sound action="a person shifting under a blanket" --sound surface=futon \
    --sound contact=soft --duration 2
```

```
a person shifting under a blanket, on futon, soft, close-miked foley. About 2 seconds.
```

## 本物の sfx 6 本（stable_audio・50 ステップ）

同じ Rule 経路を `--provider stable_audio` で通したもの。プロンプトは Spec の
意味フィールドから組み立てられ、英語の一文になる。

```bash
bin/asset.py --type sfx --project demo --scene samples --name sfx-switch-click \
    --resolve rule --provider stable_audio --seed 325 --duration 1 \
    --sound event="a light switch clicking on" --sound distance=near \
    --sound intensity=0.3
```

```
a light switch clicking on, near perspective, intensity 0.30, single sound effect. About 1 second.
```

実測（`bin/probe.py`）:

| ファイル | 起伏 `burst_db` | 無音率 | 帯域 低/中/高 dB | 重心 | 立ち上がり/減衰 | 読み |
| --- | --- | --- | --- | --- | --- | --- |
| sfx-switch-click | 64.8 dB | 97.3% | −41.6 / −7.2 / −1.0 | 4712 Hz | 12ms / 23ms | 1 打のクリック |
| sfx-glass-break | 61.7 dB | 71.4% | −33.5 / −18.5 / −0.1 | 4736 Hz | 12ms / 209ms | 破片の散る高域 |
| sfx-door-slam | 45.7 dB | 60.4% | −2.1 / −6.6 / −10.7 | 681 Hz | 58ms / 337ms | 木の重い当たり |
| sfx-gravel-steps | 19.6 dB | 19.9% | −12.9 / −4.6 / −10.7 | 1215 Hz | 639ms / 244ms | 20 打の足音 |
| sfx-thunder-far | 35.7 dB | 36.5% | −0.2 / −14.0 / −67.9 | 107 Hz | 1.18s / 116ms | 低域の雷（`bass_heavy` `no_highs` は素材どおり） |
| sfx-paper-tear | 56.6 dB | 76.8% | −18.9 / −9.9 / −0.6 | 5774 Hz | 302ms / 81ms | 乾いた裂け |

**起伏（`burst_db`）が「点で鳴ったか」の計器。** 10ms 包絡の最大−中央値で、
クリックや打撃は 15 dB 以上、持続音は数 dB。sfx がヒスに化けていないかはここで見る。

## 統合の例

声・bgm・sfx を 1 本にした例は [../mixed-scene/](../mixed-scene/) にある。

## 再現

`params.yaml` を読めば、LLM もモデル選択も要らない。seed が固定なので同じ音が出る。

```bash
bin/regenerate.py examples/sound-samples/sfx-door-close.params.yaml --out-dir /tmp/out
# → /tmp/out/sfx-door-close.wav が元の wav と byte-identical
```

**11 本すべて**（stub 3・musicgen 2・stable_audio 6）、この再生成で sha1 が一致した。
stable_audio は同じ seed でもサンプリング回数が変われば別の音になるので、回数は
`provider_settings.steps` に書いてあり、`regenerate.py` が読み戻す。musicgen は
`tokens`（尺の丸め）と `guidance_scale` を残す。

## ライセンス

- musicgen（`facebook/musicgen-small`）の重みは **CC-BY-NC 4.0**。非商用に限る。
- stub の音は本物ではないので配布しない。
