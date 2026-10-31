# longform-floor-two-speakers — 床（beta 0.0）で二人を分ける

8 行のやりとりを、**床**（`beta` 0.0・prosody が全部プロンプトの散文由来になる段）で
二通りに組んだ。人物の高さを参照音声に任せず、Direction の `pitch` に書く試み。

| 版 | ニジ | 真白 | 尺 |
| --- | --- | --- | --- |
| `floor-two-speakers.mp3`（pitch を振る） | `pitch: high` | `pitch: very_low` | 27.1 秒 |
| `floor-two-speakers-natural.mp3`（対照） | `natural` | `natural` | 32.4 秒 |

台詞・seed・間・感情・速さは二つで同じ。違うのは `pitch` の 2 行だけ。

## 何が分かったか

床では、参照音声の高さの違いが消える（参照は 297.2 / 322.2 Hz で 25 Hz 離れているのに、
作品の中では感情の偏りを除いた二人の差が +0.1 Hz になる）。そこで高さを Direction 側へ
移した。8 行 × 2 版 × seed 1〜3（48 本）で、ニジ − 真白 の f0 の差を測った。

| 行の組 | pitch を振る | 対照 |
| --- | --- | --- |
| もしもし。/ ……まだ起きてたの。 | +23.2 Hz | −3.8 Hz |
| うん。眠れなくて。/ そう。 | +48.0 Hz | −16.5 Hz |
| そっちは。/ こっちも、同じ。 | +51.5 Hz | +67.2 Hz |
| じゃあ、ちょっとだけ。/ ちょっとだけ。 | +35.0 Hz | +4.6 Hz |
| 12 組のうちニジが上の数 | **12/12** | 6/12 |
| 中央値 | **+41.5 Hz** | +0.5 Hz |

- **場面の中でも、二人の上下は崩れない。** pitch を振った版は 12 組すべてでニジが上。
  対照は 6/12 で、並びは感情のほうに引っ張られる（+67 の組はたまたま感情が揃っていた）。
- **ただし、狙った高さには置けない。** 1 行ずつの効き方は −36 〜 +28 Hz に散る。
  4 感情 × pitch 3 段 × seed 3（36 本）で測ると、neutral は very_low → high が +68.4 Hz
  なのに、sadness は +9.4・anxiety は +13.7。**もう高い台詞には、足す余地がない。**
- **pitch の語は時間も動かす。** 1 行の実験では very_low 3.25 秒 / natural 2.25 秒。
  場面では逆に pitch 版が短い（声の合計 49.3 対 63.0 秒）。一定の向きではない。
- **この段の MFCC 距離は読まない。** very_low が 22.7 で参照にいちばん近く出る
  （natural 69.9・high 81.8）。pitch をまたぐと MFCC は声質の距離にならない。

## 限界

- **人が聴いて確かめた版ではない。** 自動の測定だけを通した。
- 床の声は参照から遠い（作品版の MFCC 距離は 64.6）。配布用ではない。
- 二人を分けているのは高さだけではない。作品では帯域（`voice_fx.yaml`）でも分けている。

## 置いてあるファイル

| ファイル | 中身 |
| --- | --- |
| `floor-two-speakers.mp3` / `floor-two-speakers-natural.mp3` | 完成音（44.1kHz stereo / 192 kbps） |
| `script-pitch.yaml` / `script-natural.yaml` | 台詞と演技。違いは `pitch` の 2 行 |

## 作り方

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/floor-two-speakers
PYTHONPATH=. $PY projects/longform/assemble.py --dir projects/longform/floor-two-speakers
```

48 本の測定は `projects/longform/floor-pitch-pairs/`（`probe.tsv` と `script.yaml`）、
1 行ずつの効き方は `projects/longform/acting-floor-pitch/` と
`projects/longform/acting-pitch-emotion/`。
