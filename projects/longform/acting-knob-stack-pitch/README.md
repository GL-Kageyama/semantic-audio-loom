# 高さを振っても、演技の型は半分残る（速さほどは消えない）

`acting-knob-stack/` で、`speed` の両端では `delivery: aggressive` の差が消えた
（+6.7 → +0.7 → −1.1 Hz）。速さの端は f0 も動かすので、**「高さそのものを振っても
型は消えるのか」**を同じ条件で測った。`pitch` を low / natural / high に振り、
`delivery` を gentle / aggressive にして、seed 1〜5 で 30 本。

| pitch | delivery | 長さ (s) | f0 (Hz) | 抑揚 (半音) |
| --- | --- | --- | --- | --- |
| low | gentle | 3.20 | 310.8 | 8.00 |
| low | aggressive | 3.19 | 317.8 | 7.60 |
| natural | gentle | 3.16 | 318.6 | 7.94 |
| natural | aggressive | 3.18 | 325.3 | 7.92 |
| high | gentle | 3.17 | 321.5 | 8.02 |
| high | aggressive | 3.18 | 324.3 | 8.00 |

## aggressive − gentle は、natural でいちばん大きい

| pitch | 平均 | 中央値 | seed 5 を除いた平均 | 同符号 |
| --- | --- | --- | --- | --- |
| low | +7.00 Hz | +3.40 Hz | **+3.03 Hz** | 5/5（p = 0.15） |
| natural | **+6.68 Hz** | **+6.80 Hz** | +6.65 Hz | 5/5（p = 0.0085） |
| high | +2.86 Hz | +2.10 Hz | +2.83 Hz | 4/5（p = 0.085） |

- **低い側の平均 +7.00 は seed 5 が作っている**（seed 5 だけ +22.9 Hz、ほかは +2.0〜+3.9）。
  **中央値では +3.40**。だから平均で語らない。
- 中央値で見ると **low +3.40・natural +6.80・high +2.10**——**natural から離れると半分になり、
  0 にはならない。**
- 速さの端では 0.1 Hz まで一致した。**高さの端では一致しない。**
  つまり**消しているのは「高さ」ではなく「速さ」**（少なくとも、速さのほうが強い）。

## pitch そのものは、3 語で 10.7 Hz

| pitch | f0 (Hz) | natural との差 |
| --- | --- | --- |
| low | 310.8 | −7.8 |
| natural | 318.6 | — |
| high | 321.5 | +2.9 |

- **下への 1 段のほうが、上への 1 段より大きい**（−7.8 対 +2.9）。
  5 段の欄だが、**3 語で 10.7 Hz**（`acting-delivery/` の flat 1 語ぶん、−18.4 Hz より小さい）。
- **上へは 2.9 Hz しか動かない。** seed ごとの high − natural は +2.1 / +1.8 / 0.0 / +8.2 / +2.2 Hz。
  **上げたいときは `speed`（遅い端と速い端で +17 Hz）のほうが強い。**
- ⚠️ **delivery が controlled だと、もっと動く**（`acting-knob-stack-speed-pitch/`・
  seed 10 本）：low −13.5 Hz・high −0.1 Hz。**pitch の効きは delivery でも変わる。**
- ⚠️ **この非対称は感情で入れ替わる。** neutral の声では high が +18.8 Hz 動いた
  （264.0 → 282.8 Hz・REPORT「欄ごとの段」）。joy・moderate では上より下が動く。
  **pitch の段を、感情をまたいで 1 つの数で語らない。**

## 何が言えるか

- **交互作用の向きは一様でない。** speed は aggressive を消す。pitch は半分にする。
  下へ動く型（cold / flat）は speed でも消えない（`acting-knob-stack-cold/`）。
- 実務では、**aggressive を使いたいなら `speed: natural` のまま置く**。
  速さを端まで振る場面では、`aggressive` と書いても gentle と同じ声になる。
- **pitch は、pitch の語数を信じて使わない。** 3 語で 10.7 Hz は、
  同じ欄の `flat` 1 語より小さい。

## 限界

- 1 行・1 人物（mashiro）・1 感情（joy）。`delivery` は 2 語だけ。
- pitch の段は 3 語（5 段のうち low / natural / high）だけ測った。
- low の p = 0.15 は **5/5 だが有意でない**。差を「出た」と書かないための欄。
- 測ったのは f0・長さ・抑揚だけ。

## 測る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/acting-knob-stack-pitch
PYTHONPATH=. $PY bin/act_probe.py --tsv projects/longform/assets/acting-knob-stack-pitch/voice/*.wav \
  > projects/longform/acting-knob-stack-pitch/probe.tsv
PYTHONPATH=. $PY projects/longform/check_script_sync.py --dir projects/longform/acting-knob-stack-pitch
```
