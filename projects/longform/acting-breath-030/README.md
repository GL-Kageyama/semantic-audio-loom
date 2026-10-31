# beta 0.3 の breathiness — 段にはならないが、slight だけは 5/5 で動く

`acting-breath/` は beta 0.3 で seed 3 本しか振っておらず、差を見つけられなかった。
`acting-breath-070/` は既定 0.7 で 4 語が単調に並ぶ。**beta 0.3 でも、seed を 5 本に
すれば段になるか**を測った（1 行「明日、また来るね。」・mashiro・neutral・controlled・
`beta` 0.3・`alpha` 0.35・seed 1〜5・4 語 × 5 = 20 本）。

| breathiness | 有声の割合 | 高域の比 | f0 (Hz) | 長さ (s) |
| --- | --- | --- | --- | --- |
| none | **0.403** | 0.0099 | 264.3 | 2.52 |
| slight | **0.375** | **0.0109** | 265.0 | 2.58 |
| moderate | 0.385 | 0.0103 | 267.8 | 2.61 |
| heavy | 0.411 | 0.0106 | **281.1** | 2.59 |

## none との対応のある差（seed 1〜5）

| 語 | 有声の割合 | 高域の比 | f0 | 長さ | energy |
| --- | --- | --- | --- | --- | --- |
| slight | **−0.028**（0/5・p = 0.017） | **+9.8%（5/5・p = 0.0001）** | +0.8（3/5） | **+0.06 秒（5/5）** | −0.48 dB（0/5・0.054） |
| moderate | **−0.018**（0/5・p = 0.023） | +3.7%（3/5） | **+3.6（5/5・p = 0.003）** | **+0.09 秒（5/5）** | −0.22 dB（2/5） |
| heavy | +0.008（4/5） | +6.9%（4/5） | **+16.9（5/5・p < 0.001）** | **+0.07 秒（5/5）** | +0.60 dB（4/5） |

- **5 本にすれば、0.3 でも見える**——slight は有声の割合（0/5）と高域の比（5/5）が
  どちらも同じ向きに出る。**seed 3 本では、この 2.8 ポイントが揺れに埋もれていた。**
- ⛔ **だが段にならない。** 有声の割合は **none 0.403 → slight 0.375 → moderate 0.385 →
  heavy 0.411** で、**heavy は none より高い**（4/5）。既定 0.7 の単調（0.276 → 0.263）
  とは、並びが違う。
- **heavy は f0 を +16.9 Hz 上げる**（5/5・p < 0.001）。0.7 では +1.7 Hz（動かない）。
  **低い beta のほうが、語が声の高さまで届く。**
- **語が増えると、どれも 0.06〜0.09 秒長くなる**（5/5）。息の分だけ発話が伸びる。

## 何が言えるか

- **「0.3 では効かない」は、seed の本数のせいだった。** 5 本にすると slight の効きは
  0.3 のほうがむしろ大きい（有声 2.8 ポイント低下・高域 +9.8%）。
- **代わりに、単調さが失われる。** 語を増やすほど息が混ざる、という前提は、
  0.3 では heavy で崩れる（有声の割合が戻る・energy が上がる）。
- **息を「段」で作るのは、どちらの beta でも無理。** 使うなら slight を固定で選び、
  段は `voice_fx` の帯域で作る。

## 限界

- `acting-breath/`（seed 1〜3）とは seed 1〜3 が同条件で、**有声の割合は小数 3 桁まで
  一致する**（none 0.353/0.424/0.421・heavy 0.343/0.426/0.433）。**同じ seed・同じ
  条件なら、別の置き場で焼いても同じ音が出る**（`HISTORY.md` の決定論の項と同じ）。
- 1 行・1 人物・1 感情（neutral）。**joy の 0.7（`acting-breath-070/`）とは条件が違う。**
- 高域の比は `acting/measure_breath.py`。耳との対応は確かめていない。

## 測る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/acting-breath-030
PYTHONPATH=. $PY bin/act_probe.py --tsv projects/longform/assets/acting-breath-030/voice/*.wav \
  > projects/longform/acting-breath-030/probe.tsv
PYTHONPATH=. $PY projects/longform/acting/measure_breath.py \
  projects/longform/assets/acting-breath-030/voice/*.wav > projects/longform/acting-breath-030/breath.tsv
```
