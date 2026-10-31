# 声量の語は、声の大きさを変えない（shout も）

Direction の `volume` は 5 語（whisper / quiet / normal / loud / shout）。台本はこれを
よく書く（演劇 89 本のうち quiet 29・normal 41・whisper 3・loud 2、解説 48 本のうち
quiet 11・normal 34・loud 3）。**5 語を振っても、声の大きさは変わらない。**
`shout` だけは高さと長さを動かすが、**大きさは動かさない**（下の節）。

## 同じ行・同じ感情で、声量だけを振る

1 行「明日、また来るね。」・mashiro・joy・moderate・seed 1〜5。`volume` だけを
whisper / quiet / normal / loud に振った 20 本（`script.yaml`）、
shout を振った 5 本（`projects/longform/experiments/delivery/acting-volume-shout/`）。

| volume | energy 中央値 (dB) | rms (dB) | f0 (Hz) | 長さ (s) |
| --- | --- | --- | --- | --- |
| whisper | −13.54 | −15.56 | 315.2 | 3.10 |
| quiet | −13.50 | −15.52 | 313.3 | 3.10 |
| normal | −13.76 | −15.60 | 314.2 | 3.06 |
| loud | −13.46 | −15.54 | 315.6 | 3.15 |
| **shout** | **−14.36** | **−16.36** | **323.8** | **3.19** |

**whisper と loud の差は energy +0.08 dB・rms +0.02 dB・f0 +0.3 Hz・長さ +0.05 秒。**
"barely above a whisper" と "loudly" が、これだけしか離れていない。

同じ語の seed 5 本の幅は energy 1.1 dB・rms 0.8 dB。**語を替えた差（0.08 dB）は、
seed を替えた差（1.1 dB）の 13 分の 1。** 語の効きは、seed の振れに完全に埋もれる。

- normal との対応のある差は loud の f0 +1.4 Hz（4/5・p = 0.018）と長さ +0.08 秒
  （5/5・p = 0.014）だけ。**どちらも「大きくなった」ではなく「少し長く・少し高く」**。
- energy の差は 4 語とも p ≥ 0.09、rms は p ≥ 0.32。

## shout だけは、高さと長さを動かす — 大きさは動かさない

shout を足すと、**5 語で唯一、normal から系統的に離れる語**になる（seed 1〜5 の対）。

| 測ったもの | shout − normal | 同じ向き | p |
| --- | --- | --- | --- |
| f0 中央値 | **+9.6 Hz** | **5/5** | **0.0060** |
| 長さ | **+0.13 秒** | **5/5** | **0.0038** |
| 無音の割合 | +0.026 | 5/5 | 0.013 |
| **energy 中央値** | **−0.6 dB** | **0/5** | 0.075 |
| **rms** | **−0.76 dB** | **0/5** | — |
| 抑揚（`f0_range_st`） | +0.06 半音 | 3/5 | 0.63 |

- **叫ぶと、高い声で長くなる。だが大きくはならない**（energy はむしろ 0.6 dB 下がる）。
  whisper の −13.54 dB より **shout の −14.36 dB のほうが小さい**（中央値）。
- 上がる幅は +9.6 Hz。**`intensity` の strong の跳ね（+8.8〜+18.3 Hz）と同じ帯**で、
  声量の語としては最大だが、演技の段としては 1 段ぶん。
- 抑揚・有声の割合は動かない。**「張り」は声質として作られていない。**

## なぜ残らないか — peak 0.95 に揃うから

Normalize（7 段フローの第 5 段）が、すべての声をピーク 0.95 に合わせる
（`semantic_audio_loom/engine/normalize.py` の `normalize()`）。25 本の peak は
**全部 0.9500**（実測）。仮にモデルが大きさを変えていても、この段で消える。

`assemble.py` はこの前提を持っている（`VOLUME_GAIN = {whisper: −10, quiet: −5,
normal: 0, loud: +3, shout: +6}`）。**聴き手が聴く声量は、演技ではなくこの 5 つの値が
決めている。** 実測は、その前提が成り立つことを確かめただけで、表の値を変える理由には
ならない。shout の +6 dB は、生の声がすでに 0.8 dB 小さいことを打ち消して余りがある。

## 何が言えるか

- **`volume` は演技のノブではなく、ミックスのノブ。** 語を台本に書くこと自体は
  意味がある（`mix.yaml` の `gain_db` になる）が、**その語で「演じさせる」ことはできない**。
- `shout` は例外のようで例外でない。**高さと長さは動くが、大きさは動かない。**
  叫びを聴かせたいなら `gain_db` で作る（それが `shout: +6` の役目）。
- 「囁く」「張る」を演技として作りたいなら、**帯域・息・速さ・長さ**の側で作る
  （whisper の実体は息の混ざりかたで、大きさではない）。
- 声量を段として聴かせたいときは、`gain_db` の表を信じるしかない。**この作品の
  ダイナミクスは、原則としてミックスで作られている。**

## 限界

- 1 行・1 人物（mashiro）・1 感情（joy）。感情によっては声量の語に反応する可能性は残る。
- 帯域処理（`voice_fx.yaml`）を経たあとの差は測っていない。ミックス前の生の声だけ。
- 「囁きらしさ」「叫びらしさ」を測る計器は無い（energy・rms・f0・抑揚・長さを見た）。
  **息の割合（`voiced_fraction`）は 5 語とも 0.26〜0.28 で動かなかった**が、これが
  聴感と一致するかは確かめていない。

## 測る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/experiments/delivery/acting-volume
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/experiments/delivery/acting-volume-shout
PYTHONPATH=. $PY bin/act_probe.py --tsv projects/longform/assets/acting-volume/voice/*.wav \
  > projects/longform/experiments/delivery/acting-volume/probe.tsv
PYTHONPATH=. $PY bin/act_probe.py --tsv projects/longform/assets/acting-volume-shout/voice/*.wav \
  > projects/longform/experiments/delivery/acting-volume-shout/probe.tsv
```
