# longform — 5〜10 分の音を 2 本つくる

このディレクトリは「長尺をつくるときの型」の実例。声だけの素材ではなく、
**間・音量・音色を設計して 1 本に組む**ところまでを扱う。

台本の書き方（どの字面・欄が声を動かすか）は [scripting.md](scripting.md) に 1 枚でまとめた。

| 作品 | 中身 | 尺 |
| --- | --- | --- |
| `explainer/` | 解説「音は、なぜ感情を動かすのか」。語り手＋実例 4 本だけ真白 | 約 5 分 |
| `drama/` | 二人芝居「午前二時の電話」。真白とニジ | 約 5 分 |
| `acting-demo/` | 聞き比べ「明日、また来るね。」声の混ぜ方（`beta`）0.7 と 0.3 | 74 秒 |
| `acting-floor/` | 聞き比べの拡張。同じ一言を `beta` 0.7 / 0.3 / 0.0 で並べる | 71 秒 |
| `drama-beta03/` | 同じ脚本の演劇を `beta` 0.3 で組み直した版（聞き比べ用） | 約 5.5 分 |
| `drama-beta00/` | 同じ脚本を床（`beta` 0.0）で組み直した版（演技の上限を見る） | 約 5.7 分 |
| `floor-two-speakers/` | 床で二人を分ける聞き比べ。`pitch` を人物に振る版と、二人とも natural の対照 | 27 秒 / 32 秒 |
| `drama-beta00-pitch/` | 同じ脚本を床のまま `pitch` で二人に振った版（作品の段での効きを見る） | 約 4.9 分 |

聞き比べの見本と実測は [examples/longform-acting/](../../examples/longform-acting/)、
[examples/longform-acting-floor/](../../examples/longform-acting-floor/)、
[examples/longform-drama-beta03/](../../examples/longform-drama-beta03/)、
[examples/longform-floor-two-speakers/](../../examples/longform-floor-two-speakers/)、
[examples/longform-drama-pitch/](../../examples/longform-drama-pitch/)。
欄の見本は [examples/longform-knobs/](../../examples/longform-knobs/)（69 秒）と
[examples/longform-stack-demo/](../../examples/longform-stack-demo/)（45 秒）と
[examples/longform-delivery-speed/](../../examples/longform-delivery-speed/)（54 秒）と
[examples/longform-emotions/](../../examples/longform-emotions/)（75 秒）と
[examples/longform-pitch/](../../examples/longform-pitch/)（47 秒）と
[examples/longform-seed/](../../examples/longform-seed/)（42 秒・seed だけを振る）と
[examples/longform-subtext/](../../examples/longform-subtext/)（42 秒・裏の意味だけを振る）と
[examples/longform-punctuation/](../../examples/longform-punctuation/)（46 秒・文末の記号だけを振る）と
[examples/longform-punctuation-shape/](../../examples/longform-punctuation-shape/)（60 秒・途中の句点で効きが落ちる）と
[examples/longform-ellipsis/](../../examples/longform-ellipsis/)（34 秒・`…` は間を作らない）と
[examples/longform-punctuation-pitch/](../../examples/longform-punctuation-pitch/)（38 秒・記号は `pitch` を振っても残る）と
[examples/longform-floor-mark/](../../examples/longform-floor-mark/)（33 秒・床では `！` が消える）。

## 置き場

```
projects/longform/
  STATE.md            現在地と実測（再開するときはここから）
  timings.tsv         生成 1 回 1 行（日付・段・素材・モデル・設定・実時間・マシン）
  baseline.md         examples/ 37 本の基準線
  listening.md        聴きどころ（時刻つき。どの測った値から選んだかを並べてある）
  acting/             P1・P2 の演技実験（行列と測定。`knob_audit.py` は台本の語の数え上げ）
  drama-level/       演劇の三つの版（beta 0.7 / 0.3 / 0.0）のキューごとの測定
  explainer-level/   解説 48 本の測定（語り手と真白は包絡で分かれる）
  timbre-two-characters/  二人の声が声そのもので分かれるか（18 本）
  drama-beta00-pitch/ 床の芝居に pitch を振った版と、89 キューの測定
  seed-robustness/   床の芝居を seed 1〜3 で作り、作品の段の数が動くかを見る
  explainer-joy/     同じ 1 行で seed と方向を振る（seed のほうが f0 を動かす）
  emotion-seed/      2 行 × 5 感情 × 3 seed。seed をブロックにして感情の効きを測る
  seed-voices/       4 つの声 × seed 3。seed の癖が声をまたぐかを見る
  acting-intensity/  強度は何段か（低い beta の 90 本と、既定 0.7 の 60 本の読み方）
  acting-overwhelming-070/  既定 0.7 で overwhelming だけを seed 5 で作った 15 本
  acting-intensity-sadness/ sadness の上端を beta 0.3 で確かめる 6 本
  acting-mod-phrase/ 強度の真ん中に文言を置いた 15 本（原本は触らず、表を差し替える）
  acting-sadness-heldback/  acting-sadness-open/  sadness の真ん中に「抑える」「開く」を置いた各 5 本
  acting-anger-heldback/    anger でも「抑える」を試した 5 本
  acting-intensity-line2/   2 行目で強度 4 段 × 3 感情 × seed 5（形が台詞に依るか）
  acting-longline/          芝居の長い行（24 文字）で強度 4 段 × 3 感情 × seed 5
  acting-niji-intensity/    niji の声で subtle / moderate × 3 感情 × seed 5（2 段は声に依るか）
  acting-joy-heldback/      joy でも「抑える」を試した 5 本
  acting-volume/            声量 4 語 × seed 5（声は大きさを変えるか。shout は下）
  acting-volume-shout/      shout × seed 5（叫ぶと、高く長くなるが大きくはならない）
  acting-inton-070/         intonation 5 語（語尾の傾きは語の名前に従わない）
  acting-intonation2/       intonation の残り 2 語（neutral / wavering）
  acting-delivery/          delivery 6 語 × seed 5（12 語のうち声が動くのは何語か）
  acting-delivery2/         delivery の残り 6 語 × seed 5
  acting-speed/             speed 5 語 × seed 5（5 語とも段になるか）
  acting-speed-emotions/    anger / sadness × speed 5 語 × seed 5（段は感情に依るか）
  acting-speed-longline/    芝居の長い行（24 文字）で speed 5 語 × seed 5（段は台詞の長さに依るか）
  acting-knob-stack/        speed × delivery の 2 × 2 × seed 5（上へ動く型は速さの端で消える）
  acting-knob-stack-cold/   speed 3 段 × cold / flat × seed 5（下へ動く型は消えない）
  acting-knob-stack-pitch/  pitch 3 段 × aggressive × seed 5（半分だけ残る）
  acting-knob-stack-speed-pitch/  speed × pitch × seed 10（強い欄どうしは足し算にならない）
  acting-pitch-ladder/      pitch 6 語 × seed 10（下がる語は 3 つ、上がる語は無い）
  acting-emotion-ladder/    emotion 11 語 × seed 5（neutral より上へは動くが、隣どうしは同じ）
  acting-emotion-delivery/  emotion 3 語 × delivery 3 語 × seed 5（型を足しても隣どうしは離れない）
  determinism/              同じ Spec・同じ seed を別プロセスで N 回（再現性の検査）
  determinism/within_process.py  1 プロセスの中で N 回（1 回目だけが違う）
  acting-subtext/           subtext 5 通り × seed 5・llm 解決・1 欄ずつ（subtext が届く範囲）
  acting-freetext/          散文を 1 文だけ足す × seed 5（表に無い語彙は演技になるか）
  acting-pauses/            読点を 1 / 2 / 3 個 × seed 5（読点は間になるか）
  acting-punctuation/       文末の記号（。／？／！／なし）× seed 5（字面で動くのは何か）
  acting-punctuation-stack/ 文末の記号 × 感情の 2 × 2 × seed 5（足し算になるか）
  acting-punctuation-pitch/ 文末の記号 × pitch 3 段 × seed 5（欄と掛けても効くか）
  acting-punctuation-floor/  文末の記号 × beta 3 段 × seed 5（床で `！` は消え `？` は残る）
  acting-punctuation-long/  24 文字の行で文末の記号 × seed 5（長い行でも効くか・途中の句点の対照）
  acting-punctuation-mid/   14 文字の行で `。` / `！` × seed 5（真ん中の長さ）
  acting-punctuation-period/  9 文字のまま途中を句点にした行（途中の切れ目の効果）
  acting-punctuation-ellipsis/  文末を `…` にした 5 本（`…` は声になるか）
  acting-punctuation-ellipsis-mid/  途中の `…` の 5 本（読点に化ける・行が 0.85 秒縮む）
  acting-notation/          かな/カナ/漢字と読点 1 個 × seed 5（表記は効くか）
  acting-breath-070/        breathiness 4 語 × seed 5（息は有声の割合に出るか）
  acting-breath-030/        breathiness 4 語 × seed 5 を beta 0.3 で（0.3 では段にならない）
  acting/measure_breath.py  高域の比を出す（息の計器）
  intensity-demo/    強度の段だけを並べた 63 秒の見本（語り手の札つき）
  knob-demo/         速さ 5 語と演技の型 3 語を並べた 69 秒の見本
  stack-demo/        速さ × 演技の型の 6 通りを並べた 45 秒の見本
  delivery-speed-demo/  速さ × 3 語（gentle/aggressive/flat）を並べた 54 秒の見本
  emotion-demo/      感情 11 語を 1 本ずつ並べた 75 秒の見本（語り手の札つき）
  pitch-demo/        音の高さ 6 語を低い順に並べた 47 秒の見本
  seed-demo/         同じ指示のまま seed 1〜5 を並べた 42 秒の見本
  subtext-demo/      subtext だけを替えて 5 本並べた 42 秒の見本（同じ音になる）
  punctuation-demo/  文末の記号を替えて 8 本並べた 46 秒の見本
  punctuation-shape-demo/  同じ `！` で行の形だけを替えた 60 秒の見本（途中の句点）
  ellipsis-demo/      `…` が消える・読点になることを並べた 34 秒の見本
  punctuation-pitch-demo/  記号 × `pitch` を並べた 38 秒の見本（joy では欄が動かない）
  floor-mark-demo/    記号を演技の層の有無で並べた 33 秒の見本（床では `！` が消える）
  drama-s2/          既定 0.7 の芝居を seed 2 で作ったもの（drift の測定用・声だけ）
  drama-seed-split/  演劇のニジだけ seed 2 にした版（人物を seed で分けられるか）
  acting-breath-s70/ 芝居 s70 の 1 行で breathiness だけを none / slight に振る（6 本）
  acting-breathness-recheck/  古い take に breathiness が無かった影響を確かめる 7 本
  explainer/  drama/  作品。script.yaml が台詞と演技、mix.yaml は組み立てが書く
  assemble.py         両作品を組む道具（切る・並べる・利得・効果音・下地）
  check_render.py     門の数を測る（尺・クリップ・無音・効果音の立ち上がり）
  check_script_sync.py 台本と焼いてある声が同じかを 1 欄ずつ突き合わせる
  check_loudness.py   音量を配布の目安と比べる（LUFS・トゥルーピーク・LRA）
  deliver.py          配布用の mp3 を書く（直線のゲインだけ・チャンネル数はマスターのまま）
  near_duplicates.py  作品の中の「ほぼ同じ声になった組」を総当たりで探す
  measure_timbre.py   声のスペクトルの距離（有声フレームだけ。無音を混ぜない）
  measure_envelope.py LPC 包絡の距離（pitch に引っ張られない声質の測り方）
  check_timbre_metric.py  上の計器が無音の割合で動かないことの検査
```

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
