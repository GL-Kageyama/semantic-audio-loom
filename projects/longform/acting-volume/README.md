# 声量の語は、声の大きさを変えない

Direction の `volume` は 4 語（whisper / quiet / normal / loud）。台本はこれを
よく書く（演劇 89 本のうち quiet 29・normal 41・whisper 3・loud 2、解説 48 本のうち
quiet 11・normal 34・loud 3）。**語を振っても、声の大きさは変わらない。**

## 同じ行・同じ感情で、声量だけを振る

1 行「明日、また来るね。」・mashiro・joy・moderate・seed 1〜5。`volume` だけを
whisper / quiet / normal / loud に振った 20 本（`script.yaml`）。

| volume | energy 中央値 (dB) | rms (dB) | f0 (Hz) | 長さ (s) |
| --- | --- | --- | --- | --- |
| whisper | −13.54 | −15.56 | 315.2 | 3.10 |
| quiet | −13.50 | −15.52 | 313.3 | 3.10 |
| normal | −13.76 | −15.60 | 314.2 | 3.06 |
| loud | −13.46 | −15.54 | 315.6 | 3.15 |

**whisper と loud の差は energy +0.08 dB・rms +0.02 dB・f0 +0.3 Hz・長さ +0.05 秒。**
"barely above a whisper" と "loudly" が、これだけしか離れていない。

同じ語の seed 5 本の幅は energy 1.1 dB・rms 0.8 dB。**語を替えた差（0.08 dB）は、
seed を替えた差（1.1 dB）の 13 分の 1。** 語の効きは、seed の振れに完全に埋もれる。

- normal との対応のある差は loud の f0 +1.4 Hz（4/5・p = 0.018）と長さ +0.08 秒
  （5/5・p = 0.014）だけ。**どちらも「大きくなった」ではなく「少し長く・少し高く」**。
- energy の差は 4 語とも p ≥ 0.09、rms は p ≥ 0.32。

## なぜ残らないか — peak 0.95 に揃うから

Normalize（7 段フローの第 5 段）が、すべての声をピーク 0.95 に合わせる
（`semantic_audio_loom/engine/normalize.py` の `normalize()`）。20 本の peak は
**全部 0.9500**（実測）。仮にモデルが大きさを変えていても、この段で消える。

`assemble.py` はこの前提を持っている（`VOLUME_GAIN = {whisper: −10, quiet: −5,
normal: 0, loud: +3}`）。**聴き手が聴く声量は、演技ではなくこの 5 つの表が決めている。**
実測は、その前提が成り立つことを確かめただけで、表の値を変える理由にはならない。

## 何が言えるか

- **`volume` は演技のノブではなく、ミックスのノブ。** 語を台本に書くこと自体は
  意味がある（`mix.yaml` の `gain_db` になる）が、**その語で「演じさせる」ことはできない**。
- 「囁く」「張る」を演技として作りたいなら、**帯域・息・速さ・長さ**の側で作る
  （whisper の実体は息の混ざりかたで、大きさではない）。
- 声量を段として聴かせたいときは、`gain_db` の表を信じるしかない。**この作品の
  ダイナミクスは、原則としてミックスで作られている。**

## 限界

- 1 行・1 人物（mashiro）・1 感情（joy）。感情によっては声量の語に反応する可能性は残る。
- 帯域処理（`voice_fx.yaml`）を経たあとの差は測っていない。ミックス前の生の声だけ。
- 「囁きらしさ」を測る計器は無い（energy・rms・f0・長さを見た）。**息の割合
  （`voiced_fraction`）は 4 語とも 0.27〜0.28 で動かなかった**が、これが聴感と
  一致するかは確かめていない。

## 測る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/acting-volume
PYTHONPATH=. $PY bin/act_probe.py --tsv projects/longform/assets/acting-volume/voice/*.wav \
  > projects/longform/acting-volume/probe.tsv
```
