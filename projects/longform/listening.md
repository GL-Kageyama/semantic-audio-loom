# 聴きどころ — 戻ってきたら、ここから

**人が聴いて確かめた版ではない。** 時刻は `mix.yaml` の開始位置そのままで、
「なぜここを選んだか」はすべて測った値。耳でたしかめる順に並べた。

まず 3 か所だけ聴くなら：**演劇 0:33.7**（怒っても声が低い）・**解説 2:41〜3:18**（同じ一行の三通り）・
**演劇 4:40.7**（いちばん高い声・453 Hz）。

## 1. 演劇「午前二時の電話」`examples/longform-drama/drama.mp3`（5:10）

| 時刻 | 何が起きる | 測った根拠 |
| --- | --- | --- |
| 0:04.7 | 開幕「……もしもし。」真白 | — |
| 0:08.1 | ニジの声が電話の帯域になる（320 Hz〜3.4 kHz） | 低域 −5.3 dB・高域 −9.3 dB |
| 0:33.7 | 真白が怒る（s09）——**声は高くならない** | 267.8 Hz（真白の平均 301.7 より低い） |
| 1:18.7 | ニジ「今じゃないと、出られなかった。」 | 抑揚 11.0 半音（作品で最大） |
| 1:35.4〜2:23.1 | 軽口の往復（y01〜y17）。「猫」の話 | — |
| 2:39.9 | 真白 anger / strong / aggressive | — |
| 3:51.7 | ニジが落ちる（s52） | 258.7 Hz（ニジの平均 315.6 より低い） |
| 4:33.9 | 真白 fear / strong（s65） | 309.4 Hz（`strong` でも上端ではない） |
| **4:40.7** | 真白「ニジ！」（s67・fear / **overwhelming**） | **作品でいちばん高い 453.1 Hz** |
| 4:47.6 | **開幕と同じ一行**がもう一度（s68） | 開幕と**同じ音**（MFCC 0.00） |
| 5:05.8 | 「おやすみ。」で終わる（s72） | 抑揚 3.7 半音（作品で最小） |

## 2. 解説「音は、なぜ感情を動かすのか」`examples/longform-explainer/explainer.mp3`（5:11）

| 時刻 | 何が起きる | 測った根拠 |
| --- | --- | --- |
| 0:02.2 | 語り手の第一声 | f0 257.2 Hz・抑揚 10.5 半音 |
| 1:45.2 | 扉の音（q01）から「間」の実演へ。5.1 秒の穴 | 最長の無音 5.14 秒 |
| 2:35.2 | 「では、同じ台詞を三通りで」 | — |
| **2:41.1** | 真白 m01「明日、また来るね。」（素）。語り手から声が変わる | 声質は 4.68 dB 離れ（語り手の中の広がりは 1.40）・f0 326.0 Hz |
| **2:49.4** | m02（励まし） | 355.5 Hz・抑揚 9.6 |
| **3:00.1** | m03（別れ） | 351.4 Hz・抑揚 8.2・速さ 4.3 |
| **3:14.2** | m04（照れ隠し）——**m02 とほぼ同じ音** | 357.5 Hz・MFCC 5.6（8.0 未満） |
| 3:30.2 | 章の頭（x01）「喜怒哀楽に収まらない感情」 | 語り手でいちばん低い 237.9 Hz |
| 4:59.5 | 結び | — |

3:14 が 2:49 と似て聞こえるのは測りまちがいではない。方向を振った 5 通りの中で、
この 2 本がいちばん差の小さい選び方だった（`explainer-joy/`）。

## 3. 同じ台本の 3 版（beta 0.7 / 0.3 / 0.0）

`drama.mp3`（0.7・5:10）／`drama-beta03.mp3`（0.3・5:32）／`drama-beta00.mp3`（0.0・5:39）。
頭の 30 秒を聴き比べると分かる。**beta を下げるほど演技は伸び、声は参照から離れる。**

## 4. pitch 版（0.0＋pitch）`examples/longform-drama-pitch/drama-beta00-pitch.mp3`（4:51）

`drama-beta00.mp3` と同じ台本で、真白を `very_low`・ニジを `high` に振った版。
**上下は開く**（二人の差 +0.1 → −13.4 Hz・21/42 → 31/42）が、**真白の声の長さが 33.6% 縮み**、
尺が 5 分を割る。短くなるのは長い（静かな・遅い）テイクから。

## 5. 短い見本

- `examples/longform-acting/acting-demo.mp3`（1:14）——同じ一行 5 本を、beta 0.7 と 0.3 で。
- `examples/longform-acting-floor/acting-floor.mp3`（1:11）——同じ 3 本（無表情・喜び・怒り）を
  0.7 / 0.3 / 0.0 の三つの段で。
- `examples/longform-floor-two-speakers/floor-two-speakers.mp3`（0:27）と
  `…-natural.mp3`（0:32）——pitch を振った組と、振らない組。
- `examples/longform-intensity/intensity-demo.mp3`（1:03）——同じ一行の強度だけを
  「うすい・ふつう・つよい・さいだい」と並べた。**0:10.8 と 0:16.6 が同じに聞こえ、
  0:16.6 → 0:22.4 で跳ね、0:48.3 が 0:42.0 より低い**のが、測った段の数
  （`acting-intensity/`）。
- `examples/longform-seed/seed-demo.mp3`（0:42）——**同じ指示のまま seed だけ**を
  seed 1〜5 に振った。f0 が **258.7〜351.4 Hz（92.7 Hz）**・長さが 2.75〜3.37 秒で動く。
  **欄を 1 つ振った差（`pitch` 15.6・感情 25.5・`delivery` 45 Hz）より大きい**
  （`seed-demo/`・`acting-emotion-ladder/`）。
- `examples/longform-subtext/subtext-demo.mp3`（0:42）——**裏の意味だけ**を振った 5 本。
  **5 本とも同じ音**（`md5 f17a1f6` が 5 つ）。rule の解決では subtext が散文に載らない
  （`acting-subtext/`）。
- `examples/longform-punctuation/punctuation-demo.mp3`（0:46）——同じ 1 行の**文末だけ**を
  `。` / `？` / `！` / なしに振った。**`！` の 2 本がいちばん高い**（359.6 / 341.4 Hz）・
  **記号なしの seed 3 がいちばん低い**（260.2 Hz）。**記号は間ではなく高さを動かす**
  （`punctuation-demo/`・`acting-punctuation/`）。
- `examples/longform-punctuation-shape/punctuation-shape-demo.mp3`（1:00）——同じ `！` で
  終わる 4 種の行を、**途中が読点か句点か**だけ替えて並べた。**同じ seed で、句点の側が
  毎回低い**（seed 1：359.6 → 333.6 Hz）。**末尾の記号より、途中で切れていないこと**
  が効いている（`punctuation-shape-demo/`・`acting-punctuation-period/`）。
- `examples/longform-ellipsis/ellipsis-demo.mp3`（0:34）——**`…` は間を作らない**。
  文末の `…` と `なし` は同じ台詞・同じ seed で、**同じ高さ・同じ長さ**（320.4 Hz・
  2.50 秒）。途中の `…` は読点に化けて **1.95 秒**へ縮む。言いよどみは
  `pause_before` で作る（`ellipsis-demo/`・`acting-punctuation-ellipsis-mid/`）。
- `examples/longform-punctuation-pitch/punctuation-pitch-demo.mp3`（0:38）——`。` と `！` を
  **`pitch` を振って**聴く。very_low で +22.3 Hz（309.4 → 331.7）・high で +38.4 Hz
  （331.7 → 370.1）。**うしろの 2 本（0:28.0 と 0:31.1）は joy で `pitch` を上げても
  同じ音**（どちらも 351.4 Hz）——記号には効いて、欄には効かない
  （`punctuation-pitch-demo/`・`acting-punctuation-pitch/`）。
- `examples/longform-scripting/scripting-demo.mp3`（0:34）——**同じ場面を、記号の
  書き方だけ変えて**並べる（言葉は同じ・seed も同じ）。「来てくれたんだ。雨、すごいね。」
  が「来てくれたんだ！雨、すごいね！」で **274.1 → 327.8 Hz**、ニジも 269.4 → 301.5。
  変えていない行（0:12.1 と 0:27.0）は**同じ音**（319.4 Hz・2.62 秒）
  （`scripting-demo/`・`scripting.md` の指針）。
- `examples/longform-floor-mark/floor-mark-demo.mp3`（0:33）——**演技の層を切る**と
  `！` が消える。`beta` 0.7 では `。` から `！` で +33.6 Hz（326.0 → 359.6）だが、
  床では**同じ 249.9 Hz**（0:16.5 と 0:19.2）。`？` だけは床でも上がる（264.8 Hz）。
  **`！` は演技、`？` は地の読み**（`floor-mark-demo/`・`acting-punctuation-floor/`）。
- `examples/longform-knobs/knob-demo.mp3`（1:09）——同じ一行で、**速さ 5 語**と
  **演技の型 3 語**だけを振った。**速さは 0:10.3 → 0:32.5 で 4.35 秒 → 2.30 秒**、
  型は **0:43.4（やさしく）と 0:48.3（平ら）だけが違う**（`acting-speed/`・
  `acting-delivery/`）。

## 音量について

examples の mp3 は 23 本。**18 本が −16 ±1.0 LUFS**（トゥルーピーク −1.00〜−1.31 dBTP）。
未達は 5 本で、**すべてピークに当たっている**：`drama-beta00-pitch` −17.40・
`explainer` −18.16・`floor-two-speakers-natural` −17.64・`intensity-demo` −17.38・
`knob-demo` −17.10。**トゥルーピークが −1.13〜−1.27 dBTP なので、直線のゲインで
上げられるのは 0.13〜0.27 dB だけで、−16 LUFS には届かない。** そろえるには圧縮が要るので、
測る段では掛けていない（`deliver.py`・`REPORT.md` の「配布の高さ」）。
