# 下へ動く演技の型は、速さを振り切っても消えない

`experiments/basics/acting-knob-stack/` では、`delivery` の**上へ動く型**（aggressive）が `speed` の端で
消えた。`delivery` の**下へ動く型**（cold / flat）は natural でしか測っていなかった。
同じ条件（同じ行・joy・moderate・breathiness none・seed 1〜5・beta 0.7）で
`speed` 3 段 × `delivery` 3 語の 45 本を作った。

| speed | delivery | 長さ (s) | f0 (Hz) | 抑揚 (半音) | 間の割合 |
| --- | --- | --- | --- | --- | --- |
| very_slow | gentle | 4.41 | 309.9 | 8.18 | 0.23 |
| very_slow | cold | 4.29 | 299.4 | 7.76 | 0.22 |
| very_slow | flat | 4.25 | 293.5 | 7.38 | 0.21 |
| natural | gentle | 3.16 | 318.6 | 7.94 | 0.28 |
| natural | cold | 2.91 | 309.2 | 8.30 | 0.20 |
| natural | flat | 2.87 | 300.2 | 7.82 | 0.18 |
| very_fast | gentle | 2.46 | 327.1 | 8.02 | 0.23 |
| very_fast | cold | 2.35 | 316.1 | 7.56 | 0.17 |
| very_fast | flat | 2.22 | 305.7 | 7.42 | **0.12** |

## 型の効きは、3 つの速さで同じ

gentle を基準にした f0 の差（同じ seed で対にする）。

| delivery | very_slow | natural | very_fast |
| --- | --- | --- | --- |
| cold | **−10.5 Hz**（0/5・p = 0.019） | **−9.4 Hz**（1/5・p = 0.033） | **−11.0 Hz**（0/5・p = 0.015） |
| flat | **−16.5 Hz**（0/5・p = 0.0097） | **−18.4 Hz**（0/5・p = 0.013） | **−21.4 Hz**（0/5・p = 0.0081） |

- **速さが端でも、差は縮まない。** 交互作用（端の差 − natural の差）は
  cold −1.5〜−1.1 Hz（p ≥ 0.61）・flat −2.9〜+2.0 Hz（p ≥ 0.35）で、**どれも出ない。**
- flat は very_fast で**むしろ広がる**（−18.4 → −21.4 Hz・0/5）が、
  p = 0.35 で交互作用としては言えない。
- 長さも同じ向きで残る（cold −0.10〜−0.25 s・flat −0.16〜−0.29 s・すべて 0/5）。
- 間の割合の差は natural でいちばん大きく（flat −0.10・cold −0.08・p = 0.066 / 0.11）、
  端では小さい（−0.02〜−0.06・p = 0.042〜0.10）。**交互作用としては出ない。**
  ただし絶対値で見ると **very_fast の flat が 0.12 で、9 つの組のうち最も間を置かない。**
- 同じ natural の値は `experiments/delivery/acting-delivery/`（318.6 / 309.2 / 300.2 Hz）と一致する。

## 上へ動く型と、下へ動く型は、同じふるまいをしない

| delivery | natural | very_slow | very_fast |
| --- | --- | --- | --- |
| aggressive（`experiments/basics/acting-knob-stack/`） | **+6.7 Hz**（5/5） | +0.7 Hz（2/5） | −1.1 Hz（0/5） |
| cold（本実験） | −9.4 Hz（1/5） | −10.5 Hz（0/5） | −11.0 Hz（0/5） |
| flat（本実験） | −18.4 Hz（0/5） | −16.5 Hz（0/5） | −21.4 Hz（0/5） |

- **「2 つの欄は積み上がらない」は、上へ動く型にだけ言える。**
- 速さを端まで振ると、**aggressive の差は 0.1 Hz まで消える**（seed 3・5 で gentle と一致）。
  cold / flat の差は消えない。
- 理由は分かっていない。向きが違うので、f0 の上限に当たっているせいでもなさそう
  （この実験の最大 f0 は 361.7 Hz で、natural の gentle でも 359.6 Hz が出ている）。
- 読むときの注意：**消える型と消えない型がある**ので、「欄を 2 つ使うな」ではなく
  「**上へ動かす型を、速さと同時に使うときだけ効きが落ちる**」と読む。

## 別々に焼いても、同じ音が出る

natural の gentle / cold / flat は `experiments/delivery/acting-delivery/` と条件が同じ。この実験の
natural の値（318.6 / 309.2 / 300.2）は `experiments/delivery/acting-delivery/` の表と一致する。
さらに、very_slow / very_fast の gentle 10 本は `experiments/basics/acting-knob-stack/` と同じ条件なので、
**md5 を突き合わせたところ 10 本とも一致した**（別のプロセスで、別の置き場に焼いた）。
**Spec が同じなら、焼き直しても同じ音。**

## 限界

- 1 行・1 人物（mashiro）・1 感情（joy）。`delivery` は gentle / cold / flat の 3 語だけ。
- aggressive の値は `experiments/basics/acting-knob-stack/` から持ってきた（同じ行・同じ感情・同じ seed だが、
  natural の行は `experiments/delivery/acting-delivery/`、端の行は `experiments/basics/acting-knob-stack/`）。
- 測ったのは f0・長さ・抑揚・間・energy だけ。声質・息は見ていない。
- 「消える」は f0 で見た。**長さでは aggressive の差はもともと出ていない**（`experiments/delivery/acting-delivery/`）。

## 測る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/experiments/basics/acting-knob-stack-cold
PYTHONPATH=. $PY bin/act_probe.py --tsv projects/longform/assets/acting-knob-stack-cold/voice/*.wav \
  > projects/longform/experiments/basics/acting-knob-stack-cold/probe.tsv
PYTHONPATH=. $PY projects/longform/check_script_sync.py --dir projects/longform/experiments/basics/acting-knob-stack-cold
```
