# 台本の書き方 — 声を動かすのは、どこか

測った結果から、台本を書く人向けにまとめた 1 枚。数はすべて f0 の差——1 本ごとの
f0 中央値を seed 5 本で平均した値の、対の差（beta 0.7 の既定）。詳しい測定は各実験の README と
[`REPORT.md`](REPORT.md) の「答え」。

## 頼れる順

| 書くこと | 声への効き | 頼れるか |
| --- | --- | --- |
| 間（`pause_before`） | 長さそのもの。**焼いた無音 = 書いた値 + 0.08 秒**（0.0〜1.5 の 5 段で一定） | **頼れる**（台本の欄で決まる） |
| 文末を `！` に | **+39〜+79 Hz**（声によって変わる・5/5）。**beta 0.0 では 0**（演技の層が作る）。途中に句点があると +14.6〜+15.0・24 文字で +26.4 Hz | **頼れる**（向きは同じ・幅は行の形で縮む） |
| 文末を `？` に | **+16.3 Hz**（5/5）。beta 0.0 でも +13.1（地の読みが作る） | 頼れる |
| 速さ（`speed`） | 早口 5/5・間 5/5。**長さのノブ**（4.20 → 2.36 秒）で、高さは動かさない（±8 Hz まで・2 声） | **頼れる**（beta に依らない） |
| 読点を 1 個足す | **−17.0 Hz**（4/5）・長さは動かない | 向きは揃うが幅は未測 |
| 感情・強度の欄 | neutral 比 +4〜+26 Hz（10 語）・強度 +20〜+45 Hz（beta 0.3 のみ）。β 0.7 で聴こえる段は anger 2・joy 2・**sadness 3**（8〜9 Hz ずつ）。**記号と足し算**（`！` は 6 感情のどれの上でも +35〜+41 Hz） | **seed の揺れ（84.6 Hz）より小さい** |
| 声の高さ（`pitch`） | neutral で high +9.0 Hz（5/5）・very_low −13.5（1/5）。**joy では high +0.2 Hz（1/5）** | 感情が空のときだけ（感情が埋めると消える） |
| delivery | 幅 45 Hz（beta 0.3）・0.7 では揺れの中 | beta を下げるときだけ |
| 声量（`volume`） | 0（ミックスの利得で作る） | 使えない |
| 表記（かな・カナ・漢字） | 0（md5 まで同じ） | 使えない |
| 裏の意味（`subtext`） | 0（rule）・+6.9 Hz（llm の強度の段だけ） | 演出の記録としては残す |

## 実務の指針

1. **強く出したい行は、欄を振るより「！」を書く。** 途中に句点を置かない
   （9 文字でも `。` を 1 つ入れると +39.3 → +14.6 Hz）。つなぎは読点で。
   記号を重ねても増えない（`？！` は `！` と同じ）。**途中の `！` も効く**
   （+23.1・5/5・文末の 6 割。文末と重ねると +36.8 → **+61.1**——足し算。途中の `。` は
   −3.6 で上がらない・[`acting-punctuation-mid-exclaim/`](acting-punctuation-mid-exclaim/)）。
   **`？` も同じ形で効くが、`！` の 1/3**（文末 +12.1・途中 +11.9・両方 +24.9・すべて 5/5・
   [`acting-punctuation-mid-question/`](acting-punctuation-mid-question/)）。**記号の効きは `pitch` を 3 段
   振っても消えない**（+38.8〜+47.4 Hz・15/15）。**言いよどみは `…` で書いても
   間にならない**——文末なら消え、途中なら読点に化けて行が 0.85 秒**縮む**。
   間は `pause_before` で作る。
   いまの 2 作品は 137 行中 136 行が「。」で終わっていて、いちばん強いノブを使っていない。
   ⚠️ **全部の行に置かない。**山の行（s67）と次点の差の平均は、`！` を置く行が
   増えるほど縮む——**0 行 68.0 → 強い 3 行 1.0 → 全部 12 行 −43.3 Hz**（5 seed の平均）。
   **`！` は「強くする」道具でなく「ほかと差をつける」道具**
   （[`drama-scene-mark-selective/`](drama-scene-mark-selective/)・
   [`drama-scene-mark-seed/`](drama-scene-mark-seed/)）。**記号は選んで置く。**
   **山を移したいなら、足すだけでなく、もとの山から記号を外す**——s68 に足すだけだと
   4/5 でしか 1 位にならないが、s67 の `！` を `。` に戻すと 5/5 で入れ替わる
   （s68 と次点の差 −103.7 → +21.2 → +88.1 Hz・s67 は 391.0 → 288.0 Hz・
   [`drama-scene-mark-relocate/`](drama-scene-mark-relocate/)）。**狙う行を替えても同じ**
   （s60 +47.0・s66 +38.6——どちらも 5/5・[`drama-scene-mark-relocate2/`](drama-scene-mark-relocate2/)）。
   **記号は総量でなく配置。**
   **作品の台詞でも効く**——演劇の `intensity: strong` 9 行を文末だけ `！` にすると
   +15.5〜+120.2 Hz（27/27・欄は 1 つも変えない・[`acting-drama-mark/`](acting-drama-mark/)）。
   **短い行ほど大きく**（ひとことの「ニジ！」+120.2）、長い行ほど小さい（+15.5）。
   **強度の欄が弱い行でも同じ**（`subtle` 6 行の平均 +96.4・`moderate` 6 行 +70.1・
   12 行の平均がすべて正・[`acting-drama-mark-weak/`](acting-drama-mark-weak/)）——台詞を強く
   したいときは、まず文末に `！` を書く。**解説の語りでも効く**（作品の 6 行・15〜38 文字・
   +21.5〜+49.1・平均 +32.4・**30/30**・[`acting-explainer-mark/`](acting-explainer-mark/)）。
2. **間は台詞の読点で作らない。** `pause_before` と `assemble.py` で作る。
   読点は高さを下げるだけ（−17 Hz）。**書いた間は、そのまま焼ける**（0.0〜1.5 秒の
   5 段で、焼いた無音は書いた値 +0.08 秒・一定・[`pause-check/`](pause-check/)）。
3. **表記は自由。** 読みの指定が要るとき以外は、かな・漢字の選択は音に出ない。
4. **欄を効かせたいなら beta 0.3。** 0.7 では感情・強度は seed の揺れに埋もれる。
   **強度の語は 4 段あるが、届くのは anger・joy で 2 段、sadness で 3 段**
   （subtle と moderate は anger −1.3・joy +2.1 Hz でほぼ同じ段・
   [`acting-intensity-steps-new/`](acting-intensity-steps-new/)）。
   ただし字面の効き（記号）は beta 0.3 で縮む（+39.3 → +25.4 Hz）。
   **床（0.0）まで降ろすと `！` は消える**（−1.2 Hz）——`？` は残る（+13.1 Hz）。
   **`！` は演技の層が作っている。**
5. **seed は固定して読む。** seed を替えると f0 が 84.6〜92.7 Hz 動く。
   台本の比較は同一 seed で。
6. **subtext は書いてよい。** 音にはまだ乗らないが、記録として残り、
   llm 解決では強度の段に効く（+6.9 Hz）。

## 聴いて確かめる

同じ場面を、言葉は変えずに記号の書き方だけで 2 通りにした見本が
[`examples/longform-scripting/`](../../examples/longform-scripting/)（0:35）。
「。」で終わる書き方と、途中の句点を外して「！」を置いた書き方で、
真白の 1 行目が 274.1 → 327.8 Hz、ニジが 269.4 → 301.5 Hz になる。
**変えていない行は同じ音**（同じ台詞・同じ seed）。

## 出典

- 文末の記号：`acting-punctuation/`（`？` `！` なし）・`acting-punctuation-stack/`（感情との和）・
  `acting-mark-emotion5/`（6 感情 × 2 記号の 36 本）・
  `acting-punctuation-long/`（24 文字の行・`？！`・途中の句点の対照）・
  `acting-punctuation-mid/`（14 文字の行）・`acting-punctuation-period/`（9 文字で途中に句点）・
  `acting-punctuation-ellipsis/`（文末の `…`）・`acting-punctuation-ellipsis-mid/`（途中の `…`）・
  `acting-punctuation-pitch/`（`pitch` 3 段と掛けた 30 本＋joy の 15 本）・
  `acting-punctuation-floor/`（`beta` 0.0 / 0.3 / 0.5 / 0.7 の 80 本）・
  `acting-punctuation-speed/`（速さ 3 段と掛けた 30 本）・`acting-speed-voices/`（2 声 × 速さ 3 段 × 記号 2 の 36 本）・
  `acting-drama-mark/`（作品の強い 9 行 × 記号 2 × seed 3 の 54 本）・
  `acting-drama-mark-weak/`（強くない 12 行 × 記号 2 × seed 5 の 120 本）
- 表記・読点：`acting-notation/`
- 間：`acting-pauses/`・`pause-check/`（`pause_before` 5 段の焼き上がり）
- 欄の効き：`REPORT.md`「一覧（何が、どこまで効くか）」
