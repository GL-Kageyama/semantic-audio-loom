# longform — 5〜10 分の音を 2 本つくる

このディレクトリは「長尺をつくるときの型」の実例。声だけの素材ではなく、
**間・音量・音色を設計して 1 本に組む**ところまでを扱う。

台本の書き方（どの字面・欄が声を動かすか）は [scripting.md](scripting.md) に 1 枚でまとめた。
ディレクトリの地図・走らせ方・数字の読み方は [INDEX.md](INDEX.md)（別セッションが最初に読む 1 枚）。

| 作品 | 中身 | 尺 |
| --- | --- | --- |
| `explainer/` | 解説「音は、なぜ感情を動かすのか」。語り手＋実例 4 本だけ真白 | 約 5 分 |
| `drama/` | 二人芝居「午前二時の電話」。真白とニジ | 約 5 分 |
| `experiments/demos/acting-demo/` | 聞き比べ「明日、また来るね。」声の混ぜ方（`beta`）0.7 と 0.3 | 74 秒 |
| `experiments/basics/acting-floor/` | 聞き比べの拡張。同じ一言を `beta` 0.7 / 0.3 / 0.0 で並べる | 71 秒 |
| `experiments/scene/drama-beta03/` | 同じ脚本の演劇を `beta` 0.3 で組み直した版（聞き比べ用） | 約 5.5 分 |
| `experiments/scene/drama-beta00/` | 同じ脚本を床（`beta` 0.0）で組み直した版（演技の上限を見る） | 約 5.7 分 |
| `experiments/voice/floor-two-speakers/` | 床で二人を分ける聞き比べ。`pitch` を人物に振る版と、二人とも natural の対照 | 27 秒 / 32 秒 |
| `experiments/scene/drama-beta00-pitch/` | 同じ脚本を床のまま `pitch` で二人に振った版（作品の段での効きを見る） | 約 4.9 分 |

聞き比べの見本と実測は [examples/longform/acting/](../../examples/longform/acting)、
[examples/longform/acting-floor/](../../examples/longform/acting-floor)、
[examples/longform/drama-beta03/](../../examples/longform/drama-beta03)、
[examples/longform/floor-two-speakers/](../../examples/longform/floor-two-speakers)、
[examples/longform/drama-pitch/](../../examples/longform/drama-pitch)。
欄の見本は [examples/longform/knobs/](../../examples/longform/knobs)（69 秒）と
[examples/longform/stack-demo/](../../examples/longform/stack-demo)（45 秒）と
[examples/longform/delivery-speed/](../../examples/longform/delivery-speed)（54 秒）と
[examples/longform/emotions/](../../examples/longform/emotions)（75 秒）と
[examples/longform/pitch/](../../examples/longform/pitch)（47 秒）と
[examples/longform/seed/](../../examples/longform/seed)（42 秒・seed だけを振る）と
[examples/longform/subtext/](../../examples/longform/subtext)（42 秒・裏の意味だけを振る）と
[examples/longform/punctuation/](../../examples/longform/punctuation)（46 秒・文末の記号だけを振る）と
[examples/longform/punctuation-shape/](../../examples/longform/punctuation-shape)（60 秒・途中の句点で効きが落ちる）と
[examples/longform/ellipsis/](../../examples/longform/ellipsis)（34 秒・`…` は間を作らない）と
[examples/longform/punctuation-pitch/](../../examples/longform/punctuation-pitch)（38 秒・記号は `pitch` を振っても残る）と
[examples/longform/floor-mark/](../../examples/longform/floor-mark)（33 秒・床では `！` が消える）と
[examples/longform/scripting/](../../examples/longform/scripting)（35 秒・同じ場面を書き方だけで 2 通り）と
[examples/longform/speed/](../../examples/longform/speed)（46 秒・速さは長さ、記号は高さ）と
[examples/longform/mark-emotion/](../../examples/longform/mark-emotion)（50 秒・感情の上に記号を足す）と
[examples/longform/drama-mark/](../../examples/longform/drama-mark)（41 秒・作品の台詞の文末だけ `！`・音量は未達）と
[examples/longform/weak-mark/](../../examples/longform/weak-mark)（45 秒・強度の弱い行でも `！` は効く・音量は未達）と
[examples/longform/drama-scene-mark/](../../examples/longform/drama-scene-mark)（104 秒・場面まるごと文末だけ `！`・音量は未達）と
[examples/longform/drama-scene-choice/](../../examples/longform/drama-scene-choice)（173 秒・`！` の置き方 3 通り・音量は未達）と
[examples/longform/drama-relocate/](../../examples/longform/drama-relocate)（178 秒・`！` を移すと山も移る・音量は未達）と
[examples/longform/mid-mark/](../../examples/longform/mid-mark)（37 秒・文中の `！` も効く）。

## 置き場

```
projects/longform/
  README.md            つくり方（いまの機能と手順）
  REPORT.md            実測の答え（何が、どこまで効くか）
  STATE.md             現在地・この Mac・門の状態・todo
  INDEX.md             別セッションが最初に読む索引（全ディレクトリの地図）
  timings.tsv          生成 1 回 1 行（日付・段・素材・モデル・設定・実時間・マシン）
  baseline.md          examples/longform/ の全 WAV の基準線
  listening.md         聴きどころ（時刻つき。どの測った値から選んだかを並べてある）
  acting/              P1・P2 のスクリプト（`knob_audit.py` は台本の語の数え上げ）
  explainer/  drama/   作品。script.yaml が台詞と演技、mix.yaml は組み立てが書く
  experiments/<群>/<実験>/  測ったこと・見本
  assets/<作品>/       生成物（追わない）
  *.py  *.sh           組み立て・門・計器・納品の道具
```

experiments の 10 群。1 つの実験は `script.yaml`（台本）と、`probe.tsv`（測った値）か
`mix.yaml`（見本）を持つ。全ディレクトリの一覧は [INDEX.md](INDEX.md)。

| 群 | 何が入るか | 数 |
| --- | --- | --- |
| `basics/` | beta・alpha・感情・欄の組み合わせ（土台） | 25 |
| `punctuation/` | 字面（`！` `？` `…` 読点・表記） | 18 |
| `delivery/` | 速さ・声量・息・間・演技の型 | 18 |
| `scene/` | 作品まるごと・場面の記号 | 16 |
| `intensity/` | 強度の段 | 12 |
| `demos/` | 聞き比べの見本（`examples/longform/` の元） | 21 |
| `pitch/` | 高さと語尾 | 9 |
| `voice/` | 二人の声の分離・timbre | 5 |
| `analysis/` | 再現性・seed の揺れ・音量 | 4 |
| `subtext/` | 裏の意味 | 1 |

生成物は `assets/<作品>/` に階層で出る。

```
assets/<作品>/
  voice/       キュー 1 本 1 ファイル（.wav と .params.yaml）
  voice_trim/  頭尾の無音を切ったもの（組み立てが作る）
  voice_fx/    帯域処理をしたもの（voice_fx.yaml がある作品だけ）
  sfx/  bgm/   効果音・下地
  renders/     組み上げた 1 本
```

## つくる

```zsh
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python

# 1. 声（モデルのロードは 1 回。1 本 1〜2 秒）
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/explainer
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/drama

# 2. 音（stable_audio は 1 本 5〜8 分。バックグラウンドで）
./projects/longform/explainer/build_sound.sh
./projects/longform/drama/build_sound.sh

# 3. 組む
PYTHONPATH=. $PY projects/longform/assemble.py --dir projects/longform/explainer
PYTHONPATH=. $PY projects/longform/assemble.py --dir projects/longform/drama

# 4. 門を測る
PYTHONPATH=. $PY projects/longform/check_render.py \
  projects/longform/assets/explainer/renders/explainer.wav --mix projects/longform/explainer/mix.yaml
```

`build_voice.py` は既にある WAV を飛ばす（`--force` で作り直す）。
`assemble.py` は `script.yaml` の `pause_before` を正とし、キュー頭尾の無音を切ってから並べる
（切らないと間が 1 秒ずつ伸びる）。

## 作品ごとの設定

- `script.yaml` … 台詞と演技（emotion / intensity / volume / speed / pitch / delivery /
  breathiness / intonation）。`beta:` / `alpha:` を cue に書くと、その 1 本だけ声の
  混ぜ方を変える（`build_voice.py` が読む。既定は `SAL_ALPHA` / `SAL_BETA`）
- `chapters.yaml` … 章の頭の cue 名（その 1.2 秒手前にチャイム）
- `sfx.yaml` … `{file, anchor, offset, gain_db}`。anchor の cue の頭から offset 秒
- `bed_mute.yaml` … `{from, to}` の cue 対。その間だけ下地を止める（無音を聴かせる場面）
- `voice_fx.yaml` … 人物ごとの帯域処理（ニジは電話の帯域）

## Git

生のキュー（`assets/**/*.wav`）は追わない。同じ台詞・同じ seed で作り直せるため。
配布するのは組み上げた 1 本の **MP3** と、`.params.yaml`・`schema`・`mix.yaml`。

リポジトリに入れる音（配布する MP3・`examples/longform/` の見本 WAV）は **Git LFS** を通る
（規則はリポジトリ根の `.gitattributes`）。実体は GitHub の LFS ストレージに在り、
clone には `git-lfs` が要る。
