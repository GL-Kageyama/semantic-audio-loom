# 感情の 11 語：neutral より上へは動くが、隣どうしは区別できない

`emotion` は 11 語。neutral との差（対応を取れば 5/5 で上）は `experiments/basics/acting-emotions/` の 85 本で
すでに出ている（`acting/reanalyze_seeds.py`）。ここで取り直したのは**感情どうしの対応のある
比較**——11 語を 1 つの条件に並べて、同じ seed どうしを引く（同じ行・moderate・speed natural・
`delivery` controlled・breathiness none・beta 0.7・55 本）。

| emotion | f0 (Hz) | neutral との差 | 同符号 | p |
| --- | --- | --- | --- | --- |
| **fear** | **315.8** | **+25.5 Hz** | 5/5 | 6.2e−05 |
| joy | 314.2 | +23.9 Hz | 5/5 | 0.00037 |
| anger | 310.0 | +19.7 Hz | 5/5 | 0.0022 |
| excitement | 308.2 | +18.0 Hz | 5/5 | 0.0017 |
| confidence | 305.3 | +15.1 Hz | 5/5 | 0.0018 |
| anxiety | 305.2 | +14.9 Hz | 5/5 | 0.0032 |
| calm | 297.4 | +7.2 Hz | 5/5 | 0.0062 |
| loneliness | 296.7 | +6.4 Hz | 5/5 | 0.0045 |
| guilt | 295.4 | +5.1 Hz | 3/5 | 0.29 |
| sadness | 294.4 | +4.2 Hz | 5/5 | 0.016 |
| neutral | 290.3 | — | — | — |

差は **seed を揃えた対応のある差**（同じ seed どうしを引く）。同符号は上がった seed の数。

## 感情は効く（neutral に対しては、9/10 が 5/5）

- **11 語のうち 9 語が、neutral より高い。** 幅は +4〜+26 Hz。
- **`guilt` だけ揃わない**（3/5・p = 0.29）。差を「出た」と書かないための欄。
- 長さは +0.1〜+0.3 秒、抑揚は +0.1〜+0.9 半音。**動くが小さい。**

## 感情どうしは、両端だけ離れる

| 組 | 差 | 同符号 | p |
| --- | --- | --- | --- |
| fear − sadness | **+21.3 Hz** | 5/5 | 0.0001 |
| joy − sadness | +19.7 Hz | 5/5 | 0.0002 |
| fear − calm | +18.4 Hz | 5/5 | 0.0002 |
| anger − sadness | +15.5 Hz | 5/5 | 0.0021 |
| excitement − sadness | +13.8 Hz | 5/5 | 0.0015 |
| **fear − joy** | +1.6 Hz | 3/5 | 0.22 |
| **anger − excitement** | +1.7 Hz | 3/5 | 0.28 |
| **confidence − anxiety** | +0.1 Hz | 1/5 | 0.85 |

- **遠い 2 語は離れる。近い 2 語は同じ声。** 11 語は 11 段ではない。
- 順序は「fear・joy・anger … calm・loneliness・guilt・sadness・neutral」と、覚醒の
  高さの順に並ぶ。**隣どうしを書き分けても、音は同じになる。**

## 1 本ずつ聞いて、感情を当てることはできない

- **同じ条件でも、seed で 64.6〜98.0 Hz 動く**（65 本ぜんたいでは 241.4〜351.4 Hz）。
- 感情の差は最大 25.5 Hz。**seed の散らばりの 1/3 以下。**
- 11 群の一元配置分散分析は **F = 0.30・p = 0.98**——seed を誤差に置くと、感情の差は
  見えない。**対応を取ると（同じ seed どうし）読める。** 同じことは、聞き手にも言える：
  **1 本だけ聞かされて当てるのは無理で、seed を揃えて並べれば聞こえる。**

## 限界

- 1 行・1 人物（mashiro）・1 つの強度（moderate）・beta 0.7。
- seed 5 本。対応のある検定で p を出しているが、**境界の語（guilt・sadness）は
  seed を増やしてから決める。**
- 測ったのは f0 中央値・長さ・抑揚だけ。声質・息・語尾の形は見ていない。
- ⚠️ 同じ seed でも、**プロセスをまたぐと出力が一致しないことがある**
  （`experiments/analysis/determinism/`）。ここでは各条件を 1 プロセスで作っている。

## 測る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/experiments/basics/acting-emotion-ladder
PYTHONPATH=. $PY bin/act_probe.py --tsv projects/longform/assets/acting-emotion-ladder/voice/*.wav \
  > projects/longform/experiments/basics/acting-emotion-ladder/probe.tsv
PYTHONPATH=. $PY projects/longform/check_script_sync.py --dir projects/longform/experiments/basics/acting-emotion-ladder
```
