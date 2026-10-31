# longform — 索引

`projects/longform/` と `examples/longform/` を、別のセッションの AI が読むための 1 枚。
**どこに何があり、何が使えて、何を信用しないか**をここで揃える。中身の深掘りは各 README が持つ。

## 30 秒で分かること

- 目的は「声をどこまで演じ分けられるか」を f0 で測ること。作品は 5〜10 分の音 2 本
  （解説と二人芝居）で、門（尺・クリップ・無音・効果音）は通過済み。
- 測り方は**対の差**。同じ seed の 1 本どうしの f0 中央値の差を取り、5 本を平均する。
  seed を替えると 84.6 Hz 動くので、1 本の比較では何も言えない。
- 効くのは **`speed`**（長さ）と**字面**（`！`・`？`）。欄（emotion / intensity / delivery /
  pitch）は seed の揺れより小さいか、上へ動くだけで隣どうしは同じ声。
- **声量は声でなくミックス**（`assemble.py` の `VOLUME_GAIN`）。
- 裁定は下の「決めたこと」。測った値は `experiments/<群>/<実験>/probe.tsv`（74 ディレクトリ）にある。

## 読む順

| 順 | ファイル | 何に答えるか | いつ読むか |
| --- | --- | --- | --- |
| 1 | [STATE.md](STATE.md) | 現在地・この Mac の仕様・生成モデル・門の状態・todo | 作業を再開するとき |
| 2 | [REPORT.md](REPORT.md) | 答え。何が、どこまで効くか（表と根拠） | 「この値は本当か」を確かめるとき |
| 3 | [scripting.md](scripting.md) | 台本を書く人が使う 1 枚（頼れる順） | 台詞を書くとき |
| 4 | 下の「決めたこと」 | 覆すと何が崩れるか | 方針を変えたくなったとき |
| 5 | この INDEX | ディレクトリの地図・走らせ方・注意 | 見つからないとき |

補助：[README.md](README.md)（つくり方と道具）、[listening.md](listening.md)（聴きどころ）、
[baseline.md](baseline.md)（`examples/longform/` の全 WAV の基準線）。

## 決めたこと（覆すには根拠が要る）

| 決定 | 中身 | 出典 |
| --- | --- | --- |
| 既定の `beta` | 0.7。演技を伸ばして測る実験だけ 0.3 以下へ落とす | [REPORT.md](REPORT.md)「ノブ（beta）を振る」 |
| 強度の真ん中 | `_INTENSITY_PHRASES` の 4 帯すべてに一言を置く。出荷した表で作り直しても音は同じ（md5 15/15） | [experiments/intensity/acting-mod-phrase-ship/](experiments/intensity/acting-mod-phrase-ship/README.md) |
| 配布の音量 | **圧縮を掛けない**（通常盤）。`deliver.py` は直線のゲインと −1 dBTP だけ。届かない見本は未達のまま残す | [experiments/analysis/loudness-trial/](experiments/analysis/loudness-trial/README.md)・`docs/loudness.md` |
| 記号の置き方 | `！` は**選んで置く**。山と次点の差の平均は、置く行が増えるほど縮む（0 行 68.0 → 強い 3 行 1.0 → 全部 12 行 −43.3 Hz・seed 5 の平均） | [experiments/scene/drama-scene-mark-selective/](experiments/scene/drama-scene-mark-selective/README.md) |
| 声量 | 声では作らない。`assemble.py` の `VOLUME_GAIN`（−10/−5/0/+3/+6 dB）が決める | `docs/loudness.md` |
| 追うもの | 生の WAV は追わない。`probe.tsv`・`script.yaml`・README・配布 mp3（`examples/longform/`）を追う | [README.md](README.md)「Git」 |
| 置き場 | 生成物は `assets/<作品>/`（`basename` が素材名）。素材と統合（`renders/`）を混ぜない | [STATE.md](STATE.md) |

## 走らせ方

```zsh
REPO=~/AI創作工房/semantic-audio-loom
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python   # torch・numpy・jsonschema・pytest
cd $REPO

# 声（モデルのロードは 1 回・1 本 1〜2 秒）
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/drama

# 測る（演技の計器。TSV を probe.tsv として残す）
PYTHONPATH=. $PY bin/act_probe.py --tsv projects/longform/assets/drama/voice/*.wav > probe.tsv

# 組む → 門 → 配る
PYTHONPATH=. $PY projects/longform/assemble.py --dir projects/longform/drama
PYTHONPATH=. $PY projects/longform/check_render.py \
  projects/longform/assets/drama/renders/drama.wav --mix projects/longform/drama/mix.yaml
PYTHONPATH=. $PY projects/longform/deliver.py \
  projects/longform/assets/drama/renders/drama.wav examples/longform/drama/drama.mp3

# 台本と焼いてある声が同じか（1 欄ずつ）
PYTHONPATH=. $PY projects/longform/check_script_sync.py --dir projects/longform/drama

# リポジトリのテスト
PYTHONPATH=. $PY -m pytest tests/
```

### 落とし穴

1. **`--dir` は cwd からの相対**。`build_voice.py` はすぐ `basename` を素材名にするので、
   `--dir experiments/intensity/acting-intensity-steps-new` の生成物は
   `assets/acting-intensity-steps-new/voice/` に出る。**同じ `basename` を 2 つ作らない**
   （いまは重複 0）。
2. **`assets/` は `.gitignore`**（`/projects/*/assets/`）。コミットされるのは
   `probe.tsv`・`script.yaml`・`mix.yaml`・README だけ。WAV は「同じ台詞と同じ seed で
   作り直せる」ので追わない。
3. **`check_script_sync.py` は `projects/longform/` の直下**にいる（`bin/` ではない）。
4. **実験の道具は根を自分で探す**（`_lf_root()`）。ディレクトリの階層を動かしても壊れない。
   新しい道具も同じ形で書く。
5. **生成の実時間は `timings.tsv` へ 1 行**（日付・段・素材・モデル・設定・実時間・マシン）。
   マシンが違えば時間は比べられない。

## 1 つの実験の形

```
experiments/<群>/<実験>/
  script.yaml    台本（character / line / emotion / intensity / volume / speed / seed …）
  probe.tsv      測った値（act_probe.py --tsv の出力）
  README.md      何を測ったか・読み方・出典
  make_script.py 台本を組み立てる道具（ある時だけ）
  mix.yaml       聞き比べの見本の組み立て（`examples/longform/` に mp3 が出る）
```

- **測定**：`script.yaml` ＋ `probe.tsv`（＋ `README.md`）。読むのは `probe.tsv`。
- **見本**：`script.yaml` ＋ `mix.yaml`。mp3 は `examples/longform/<名>/` に置く。
- **道具つき**：上のどちらかに `measure_*.py` を足す（`emotion-seed`・`seed-voices` など）。
- 未追跡の作業ディレクトリ（`acting-subtext-reburn*`・`delivery-speed-demo-s{2,3,4}`）は
  ビルドの途中で、索引には載せない。

## experiments の地図（129 ディレクトリ）

10 群。`basics` が土台（beta・alpha・感情）、`punctuation` / `delivery` / `intensity` /
`pitch` が欄ごと、`scene` が作品まるごと、`demos` が `examples/longform/` の元、
`analysis` が再現性と音量、`voice` が声の分離、`subtext` が裏の意味。

### analysis（4）

| ディレクトリ | 何を測ったか・何の見本か |
| --- | --- |
| `determinism` | 同じ Spec・同じ seed を、プロセスを分けて何度も作る（再現性の検査） |
| `emotion-seed` | 感情の効きは、seed の揺れを超えるか |
| `loudness-trial` | 圧縮は掛けない（通常盤で配布する）——掛け方と代償は残す |
| `seed-robustness` | 作品の段の数は seed で動くか |

### basics（25）

| ディレクトリ | 何を測ったか・何の見本か |
| --- | --- |
| `acting-alpha` | alpha を振る（beta は 0.3 固定）。演技の分かれ方と参照音声への近さの両方を見る |
| `acting-alpha-floor` | 床（beta 0.0）で alpha が声の同一性をどこまで決めているか。alpha 3 段 × 参照 2 × 感情 2 × seed 3 |
| `acting-alpha-one` | 床（beta 0.0）で alpha 1.0（timbre を全部参照から）にすると声が戻るか（12 本） |
| `acting-axes` | beta 0.3 で、感情以外の Direction（声量・速さ・息・演技の型）は分かれるか |
| `acting-beta-030` | beta 掃引：alpha 0.35 固定・beta 0.30。4 感情 × seed 1〜5 |
| `acting-beta-050` | beta 掃引：alpha 0.35 固定・beta 0.50。4 感情 × seed 1〜5 |
| `acting-beta-070` | beta 掃引：alpha 0.35 固定・beta 0.70。4 感情 × seed 1〜5 |
| `acting-beta-int` | beta 0.3 で強度（subtle 0.25 / strong 0.75）が分かれるか。3 感情 × seed 5 |
| `acting-beta-lines` | 台詞を変えても beta 0.3 の覚醒の分かれ方が残るか。3 台詞 × 4 感情 × seed 1〜3 |
| `acting-beta-low` | beta をさらに下げる（alpha 0.35 固定）。0.3 より下で演技が伸びるか、壊れるか |
| `acting-beta-refs` | 別の参照音声（語り手・ニジ）でも beta 0.3 の覚醒の分かれ方が残るか |
| `acting-emotion-delivery` | 感情（neutral / joy / fear）× delivery（gentle / aggressive / cold）× seed 5 = 45 本 |
| `acting-emotion-ladder` | 感情 11 語を、seed 5 本で 1 つの条件に並べる |
| `acting-emotions` | 11 感情 × beta 0.3 / 0.0 × seed 1〜3。覚醒の先に、感情の名前が分かれるか |
| `acting-floor` | 聞き比べ：同じ一言を beta 0.7 / 0.3 / 0.0 で。台詞は「明日、また来るね。」 |
| `acting-floor-axes` | 床（beta 0.0）で感情の外の軸が効くか。条件は `acting-axes`（beta 0.3）と同一 |
| `acting-floor-lines` | 台詞を変えても beta 0.3 の覚醒の分かれ方が残るか（床） |
| `acting-floor-refs` | 別の参照音声でも beta 0.3 の覚醒の分かれ方が残るか（床） |
| `acting-freetext` | 表に無い自由文は、声を動かすか |
| `acting-knob-stack` | 速さと演技の型は、足し合わさるか（2 × 2 × seed 5） |
| `acting-knob-stack-cold` | 速さを振り切ると、下へ動く演技の型も消えるか（2 × 3 × seed 5） |
| `acting-knob-stack-pitch` | 高さを振り切ると、aggressive の効きも消えるか（3 × 2 × seed 5） |
| `acting-knob-stack-speed-pitch` | 強い欄どうしは、足し合わさるか（speed 2 × pitch 3 × seed 5） |
| `acting-matrix` | P1 の再測：11 感情（moderate）× seed 1〜5、および強度 subtle/strong × 3 感情 × seed 1〜5 |
| `alpha-07-zero` | beta 0.7 で alpha 0.0（timbre を全部プロンプトから）。3 本 |

### delivery（18）

| ディレクトリ | 何を測ったか・何の見本か |
| --- | --- |
| `acting-breath` | 息の混じり方（breathiness）を散文へ通した後、実際に音が変わるか |
| `acting-breath-030` | breathiness 4 語 × seed 5 を beta 0.3 で（`acting-breath/` は seed 3 本だけだった） |
| `acting-breath-070` | breathiness を既定の混ぜ方（beta 0.7）でも測る |
| `acting-breath-s70` | `breathiness: slight` は小さなノブか（芝居 s70 の 1 行で） |
| `acting-breathness-recheck` | 枠外 10 種のうち breathiness を slight / heavy と書いた 6 種（seed 1）を作り直す |
| `acting-delivery` | delivery の 12 語のうち、声が動くのはどれか |
| `acting-delivery2` | delivery の残り 6 語は、声を動かすか |
| `acting-dlv` | 感情と演技の型（delivery）が食い違うとき、どちらが音を決めるか |
| `acting-dlv-low` | delivery の効きは beta のどこで最大か。neutral・cold/cheerful/aggressive・seed 1〜3・beta 0.1 と 0.2 |
| `acting-longline` | 長い台詞（24 文字）でも、強度の形は同じか |
| `acting-pauses` | 読点は、間にならない |
| `acting-speed` | speed の 5 語は、速さを変えるか |
| `acting-speed-emotions` | 速さの 5 段は、感情を替えても 5 段か |
| `acting-speed-longline` | 長い台詞でも、速さは 5 段か |
| `acting-speed-voices` | 速さの効きは、声を替えても同じか（2 声 × 3 段 × 2 記号 × seed 3 = 36） |
| `acting-volume` | 声量の語は、声を小さくするか |
| `acting-volume-shout` | shout も、声を大きくしないか |
| `pause-check` | `pause_before` は、本当にその長さの間になるか（5 本） |

### demos（21）

| ディレクトリ | 何の見本か（mp3 は `examples/longform/`） |
| --- | --- |
| `acting-demo` | 同じ一言を beta 0.7 と 0.3 で（→ `examples/longform/acting/`・74 秒） |
| `delivery-speed-demo` | 速さを振り切ると、消える型と消えない型がある（→ `delivery-speed/`・54 秒） |
| `drama-mark-demo` | 作品の台詞の文末だけを `！` にする（→ `drama-mark/`・41 秒） |
| `drama-relocate-demo` | 山を移す（台本のまま／s68 に足す／s67 を戻して s68 に足す・seed 3・→ `drama-relocate/`・178 秒） |
| `ellipsis-demo` | 省略記号「…」は、間を作らない（→ `ellipsis/`・34 秒） |
| `emotion-demo` | 感情を 11 語ぜんぶ並べる（→ `emotions/`・75 秒） |
| `floor-mark-demo` | `！` は演技の層が作り、`？` は地の読みが作る（→ `floor-mark/`・33 秒） |
| `intensity-demo` | 強度はどこから声に出るか（→ `intensity/`・63 秒） |
| `knob-demo` | 声を変えるのは、どの欄か（→ `knobs/`・69 秒） |
| `mark-emotion-demo` | 感情の上に、記号を足す（→ `mark-emotion/`・50 秒） |
| `mid-mark-demo` | 文中の `！`（台本の y06・5 通り・seed 3・→ `mid-mark/`・37 秒） |
| `pitch-demo` | 音の高さの 6 語を、低い順に並べる（→ `pitch/`・47 秒） |
| `punctuation-demo` | 文末の記号だけを替える（→ `punctuation/`・46 秒） |
| `punctuation-pitch-demo` | 記号の効きは、`pitch` を振っても残る（→ `punctuation-pitch/`・38 秒） |
| `punctuation-shape-demo` | 途中に句点があると、末尾の `！` が効かない（→ `punctuation-shape/`・60 秒） |
| `scripting-demo` | 同じ場面を、記号の書き方だけで 2 通り（→ `scripting/`・35 秒） |
| `seed-demo` | 同じ指示で seed だけを替える（→ `seed/`・42 秒） |
| `speed-demo` | 速さは長さのノブ、記号は高さのノブ（→ `speed/`・46 秒） |
| `stack-demo` | 速さを端まで振ると、演技の型の差は聞こえない（→ `stack-demo/`・45 秒） |
| `subtext-demo` | subtext だけを替える（rule 解決では音が同じ・→ `subtext/`・42 秒） |
| `weak-mark-demo` | 強くない行でも、文末の 1 字で声は上がる（→ weak-mark/・45 秒） |

### intensity（12）

| ディレクトリ | 何を測ったか |
| --- | --- |
| `acting-anger-heldback` | 「the feeling is present, but held back」を anger で（5 本） |
| `acting-intensity` | 強度の段はどこまで分かれるか。5 語 × 3 感情 × beta 0.3 / 0.0 × seed 1〜3（90 本） |
| `acting-intensity-line2` | 強度の段は、台詞を替えても同じか |
| `acting-intensity-sadness` | sadness の上端だけを beta 0.3 で確かめる |
| `acting-intensity-steps-new` | 真ん中に文言を入れた後、段はいくつか（subtle / moderate / strong × 3 感情 × seed 5・45 本・**いまの値**） |
| `acting-joy-heldback` | 同じ「抑える」の一言を joy で（5 本） |
| `acting-mod-phrase` | 強度の真ん中にも散文を 1 つ置く（moderate だけを 15 本・表を差し替えて焼いた） |
| `acting-mod-phrase-ship` | 出荷した既定の表で真ん中の帯を作り直す（moderate 15 本・md5 15/15 一致） |
| `acting-niji-intensity` | ニジの声でも、subtle と moderate は同じ段か |
| `acting-overwhelming-070` | 上端：overwhelming は strong の先にあるか（既定 beta 0.7・15 本） |
| `acting-sadness-heldback` | 同じ「抑える」の一言を sadness で（5 本） |
| `acting-sadness-open` | 「the feeling is steady and open」を sadness で（5 本） |

### pitch（9）

| ディレクトリ | 何を測ったか |
| --- | --- |
| `acting-floor-pitch` | 床（beta 0.0）で、pitch が人物の高さを戻せるか。参照は二つ（真白・ニジ） |
| `acting-inton-000` | 語尾の抑揚の同じ掃引を beta 0.0 で。プロンプトが全部なら語尾も分かれるか |
| `acting-inton-030` | 語尾の抑揚（rising / flat / falling）× seed 1〜5。beta 0.3 |
| `acting-inton-070` | 語尾の抑揚（rising / flat / falling）× seed 1〜5。beta 0.7 |
| `acting-intonation2` | intonation の残り 2 語（neutral / wavering）を、既存の 3 語と同じ条件で作る |
| `acting-pitch` | beta 0.3 で下がった声域を、pitch（Direction）で戻せるか |
| `acting-pitch-emotion` | 床で pitch は感情の上に足し算で乗るか。4 感情 × pitch 3 段 × seed 3（beta 0.0） |
| `acting-pitch-ladder` | pitch の 6 語を、seed 10 本で全部振る |
| `floor-pitch-pairs` | 台詞の並びの中で、pitch の割り当てが人物を分けたまま保てるか |

### punctuation（18）

| ディレクトリ | 何を測ったか |
| --- | --- |
| `acting-drama-mark` | 作品の強い 9 行を文末だけ `！` にしたら、声は動くか（54 本） |
| `acting-drama-mark-weak` | 強くない 12 行に `！` を書いたら、声は動くか（120 本） |
| `acting-explainer-mark` | 解説の語りでも `！` は効く（作品の 6 行 × 記号 2 × seed 5） |
| `acting-floor-mark-lines` | 床で消える `！` は、別の行・別の声でも消えるか（3 行 × 2 声 × beta 2 段 × 記号 2 × seed 3 = 72） |
| `acting-mark-emotion5` | 記号は、どの感情の上にも同じだけ足せるか（6 感情 × 2 記号 × seed 3 = 36） |
| `acting-notation` | 表記は音を変えない。読点は、高さを下げる |
| `acting-punctuation` | 文末の句読点は、声を動かす（。／？／！／なし × seed 5） |
| `acting-punctuation-ellipsis` | 「…」は無視される——言いよどみは、この字面では作れない |
| `acting-punctuation-ellipsis-mid` | 途中の「…」は、間にならない——読点に化けて、行を 0.85 秒短くする |
| `acting-punctuation-floor` | 記号の効きは、声の混ぜ方（beta）の深さで残るか（4 記号 × beta 4 × seed 5 = 80） |
| `acting-punctuation-long` | 文末の記号は、長い行（24 文字）でも効くが、幅は縮む |
| `acting-punctuation-mid` | 真ん中の長さ（14 文字）では、短い行と同じ幅で効く |
| `acting-punctuation-mid-exclaim` | 文中の `！` も効く（台本の y06・5 通り × seed 5） |
| `acting-punctuation-mid-question` | 文中の `？` も効く（台本の y06・4 通り × seed 5） |
| `acting-punctuation-period` | 途中の句点 1 つで、`！` の効きは半分以下になる |
| `acting-punctuation-pitch` | 文末の記号と pitch は、足し算になるか（2 × 3 × seed 5） |
| `acting-punctuation-speed` | 速さと文末の記号は、足し算になるか（3 段 × 2 記号 × seed 5 = 30） |
| `acting-punctuation-stack` | 文末の記号と感情は、足し算になる（2 × 2 × seed 5） |

### scene（16）

| ディレクトリ | 何を測ったか・何の見本か |
| --- | --- |
| `drama-beta00` | 演劇「午前二時の電話」を床（beta 0.0）で組み直した版（声だけ・5 分 39 秒の見本は `examples/longform/drama-beta00/`） |
| `drama-beta00-pitch` | 床の芝居に `pitch` を人物へ振った版と、89 キューの測定（→ `examples/longform/drama-pitch/`） |
| `drama-beta00-s2` | 床の芝居を seed 2 で作ったもの（3 seed の比較用） |
| `drama-beta00-s3` | 床の芝居を seed 3 で作ったもの |
| `drama-beta03` | 演劇を beta 0.3 で組み直した版（→ `examples/longform/drama-beta03/`・5 分 32 秒） |
| `drama-level` | 演劇の三つの版（0.7 / 0.3 / 0.0）をキューごとに測った記録 |
| `drama-s2` | 既定（beta 0.7）の演劇を seed 2 で作ったもの（drift の測定用・声だけ） |
| `drama-scene-mark` | 場面まるごと文末を `！` にしたら、声はどう動くか（→ `examples/longform/drama-scene-mark/`・104 秒） |
| `drama-scene-mark-choice` | `！` をどこに置くか、同じ場面を 3 通り（→ `examples/longform/drama-scene-choice/`・173 秒） |
| `drama-scene-mark-relocate` | 山を動かせるか：`！` を s68 へ移す（3 通り × 13 行 × seed 5・195 本） |
| `drama-scene-mark-relocate2` | 狙う行を s60・s66 に替えても山は移るか（390 本） |
| `drama-scene-mark-seed` | 終わりの場面 13 行 × 記号 2 × seed 5（測るため・間は 0） |
| `drama-scene-mark-selective` | 強い 3 行だけに `！` を置いた場面と、台本のまま（130 本） |
| `drama-seed-split` | 演劇の台本を、ニジだけ seed 2 に替えた版（声だけ・組み立てない） |
| `explainer-joy` | 同じ 1 行で seed と演技の方向を振る（seed のほうが f0 を動かす） |
| `explainer-level` | 解説 48 キューの測定（語り手と真白は包絡で分かれる） |

### subtext（1）

| ディレクトリ | 何を測ったか |
| --- | --- |
| `acting-subtext` | subtext だけを振る（rule 解決・5 通り × seed 5 = 25 本）。subtext が声に届く範囲 |

### voice（5）

| ディレクトリ | 何を測ったか・何の見本か |
| --- | --- |
| `floor-two-speakers` | 床（beta 0.0）で二人芝居を組むとき、参照の代わりに pitch で高さを分ける |
| `floor-two-speakers-natural` | 対照：同じ台詞で pitch を二人とも natural にした版 |
| `seed-voices` | seed の癖は、声をまたぐか（4 つの声 × seed 3） |
| `timbre-beta-alpha` | MFCC 距離は beta と alpha のどちらに動かされるか。2 × 2 × seed 3（12 本） |
| `timbre-two-characters` | 二人の声が、有声フレームの距離で分かれるか（18 本） |

## examples/longform の地図（30 本）

耳で確かめる見本。各 README の冒頭に**出典（experiments のどこから作ったか）と尺**がある。
作品 2 本（`drama/`・`explainer/`）は `projects/longform/` の台本から作る。

| ディレクトリ | 何の見本か | 出典 |
| --- | --- | --- |
| `drama` | 二人芝居「午前二時の電話」（5 分 10 秒・作品） | `projects/longform/drama/` |
| `explainer` | 解説「音は、なぜ感情を動かすのか」（5 分 11 秒・作品） | `projects/longform/explainer/` |
| `drama-beta03` | 同じ脚本を beta 0.3 で組み直した版（5 分 32 秒） | `experiments/scene/drama-beta03/` |
| `drama-beta00` | 同じ脚本を床（beta 0.0）で組み直した版（5 分 39 秒） | `experiments/scene/drama-beta00/` |
| `drama-pitch` | 床の芝居に `pitch` を人物へ振った版（4 分 51 秒） | `experiments/scene/drama-beta00-pitch/` |
| `floor-two-speakers` | 床で二人を分ける（27 秒） | `experiments/voice/floor-two-speakers/` |
| `acting` | 「明日、また来るね。」を beta 0.7 / 0.3 で（74 秒） | `experiments/demos/acting-demo/` |
| `acting-floor` | 同じ一言を beta 0.7 / 0.3 / 0.0 で（71 秒） | `experiments/basics/acting-floor/` |
| `knobs` | 声を変えるのは、どの欄か（69 秒） | `experiments/demos/knob-demo/` |
| `stack-demo` | 速さを振り切ると、演技の型の差は聞こえない（45 秒） | `experiments/demos/stack-demo/` |
| `delivery-speed` | 速さを振り切ると、消える型と消えない型がある（54 秒） | `experiments/demos/delivery-speed-demo/` |
| `emotions` | 感情 11 語を 1 本ずつ並べる（75 秒） | `experiments/demos/emotion-demo/` |
| `pitch` | 音の高さの 6 語を低い順に（47 秒） | `experiments/demos/pitch-demo/` |
| `intensity` | 強度は、どこから声に出るか（63 秒） | `experiments/demos/intensity-demo/` |
| `seed` | 同じ指示で seed 1〜5 を並べる（42 秒） | `experiments/demos/seed-demo/` |
| `subtext` | subtext だけを替える（同じ音が五回・42 秒） | `experiments/demos/subtext-demo/` |
| `punctuation` | 文末の記号だけを替える（46 秒） | `experiments/demos/punctuation-demo/` |
| `punctuation-shape` | 途中の句点で `！` の効きが落ちる（60 秒） | `experiments/demos/punctuation-shape-demo/` |
| `ellipsis` | `…` は間を作らない（34 秒） | `experiments/demos/ellipsis-demo/` |
| `punctuation-pitch` | 記号の効きは `pitch` を振っても残る（38 秒） | `experiments/demos/punctuation-pitch-demo/` |
| `floor-mark` | 床では `！` が消える（33 秒） | `experiments/demos/floor-mark-demo/` |
| `scripting` | 同じ場面を書き方だけで 2 通り（35 秒） | `experiments/demos/scripting-demo/` |
| `speed` | 速さは長さ、記号は高さ（46 秒） | `experiments/demos/speed-demo/` |
| `mark-emotion` | 感情の上に記号を足す（50 秒） | `experiments/demos/mark-emotion-demo/` |
| `drama-mark` | 作品の台詞の文末だけを `！` にする（41 秒・音量は未達） | `experiments/demos/drama-mark-demo/` |
| `weak-mark` | 強度の弱い行でも `！` は効く（45 秒・音量は未達） | `experiments/demos/weak-mark-demo/` |
| `drama-scene-mark` | 場面まるごと文末だけ `！`（104 秒・音量は未達） | `experiments/scene/drama-scene-mark/` |
| `drama-scene-choice` | `！` の置き方 3 通り（173 秒・音量は未達） | `experiments/scene/drama-scene-mark-choice/` |
| `drama-relocate` | `！` を移すと山も移る（178 秒・音量は未達） | `experiments/demos/drama-relocate-demo/` |
| `mid-mark` | 文中の `！` も効く（37 秒） | `experiments/demos/mid-mark-demo/` |

「音量は未達」は、`deliver.py` が直線のゲインだけなので −16 LUFS に届いていない見本。
音を削って目安に合わせない（[experiments/analysis/loudness-trial/](experiments/analysis/loudness-trial/README.md)）。

## 数字を読むときの約束

1. **対で読む。** 同じ台詞・同じ seed の 1 本ずつを並べ、その差を 5 本平均する。
   seed をまたいだ差は 84.6 Hz 動くので、1 本ずつの比較には意味がない。
2. **md5 は「散文が同じ」の検査。** 表（`_INTENSITY_PHRASES` など）を変えると同じ seed でも別の音になる。
   `acting-intensity-steps-new` の md5 30/30 一致は、**変えていない段**の話。
3. **未達は未達。** 音量が届かない見本は「未達」と書き、音を削らない。
4. **seed 1 本の差を結論にしない。** `experiments/analysis/determinism/` が同じ Spec・同じ seed でも
   プロセスを分けると最後のビットが割れることを示している。
5. **古い節がある。** `REPORT.md` と `docs/resolve.md` の「強度は 2 段」「+6.9 Hz」は、
   真ん中の帯が空だったときの値。いまは [experiments/intensity/acting-intensity-steps-new/](experiments/intensity/acting-intensity-steps-new/README.md)
   が正で、既定 beta 0.7 で anger 2 段・joy 2 段・sadness 3 段（8〜9 Hz ずつ）。
6. **時間はマシンつきで読む。** `timings.tsv` の `machine` が違えば比べられない。
