# delivery の 12 語で、声が動くのは 4 語だけ

`delivery` は語が一番多い欄（12 語）。台本はこれもよく書く（演劇 89 本のうち
gentle 30・cheerful 14・hesitant 13・flat 9・restrained 9・cold 6・desperate 5・
aggressive 2）。**12 語を全部振ると、真ん中に 8 語が固まり、上下に 4 語が離れる。**

## 同じ行・同じ感情で、delivery だけを振る

1 行「明日、また来るね。」・mashiro・joy・moderate・volume normal・speed natural・
seed 1〜5。12 語 × 5 seed = 60 本（6 語は `script.yaml`・残り 6 語は
`projects/longform/acting-delivery2/`）。

| delivery | f0 (Hz) | gentle との差 | 同符号 | p |
| --- | --- | --- | --- | --- |
| **desperate** | **327.0** | **+8.4 Hz** | 5/5 | **0.0017** |
| **aggressive** | **325.3** | **+6.7 Hz** | 5/5 | **0.0085** |
| suppressed | 319.7 | +1.1 Hz | 3/5 | 0.20 |
| gentle | 318.6 | — | — | — |
| intimate | 317.7 | −0.9 Hz | 2/5 | 0.64 |
| cheerful | 317.5 | −1.1 Hz | 1/5 | 0.39 |
| hesitant | 317.1 | −1.5 Hz | 1/5 | 0.27 |
| restrained | 316.7 | −1.9 Hz | 1/5 | 0.17 |
| subtle | 316.6 | −2.0 Hz | 1/5 | 0.080 |
| controlled | 314.2 | −4.4 Hz | 1/5 | 0.048 |
| **cold** | 309.2 | **−9.4 Hz** | 1/5 | **0.033** |
| **flat** | **300.2** | **−18.4 Hz** | 0/5 | **0.013** |

- **真ん中に 8 語**（gentle / cheerful / hesitant / restrained / subtle / suppressed /
  intimate、±4 Hz の controlled を含む）。差は 4 Hz 以内で、**書き分けても声は同じ**。
- **上へ離れるのが 2 語**（aggressive +6.7・desperate +8.4）。どちらも **5/5 で同じ向き**。
- **下へ離れるのが 2 語**（cold −9.4・flat −18.4）。長さも縮み（−0.25・−0.29 秒・0/5）、
  無音の割合が 0.27 → 0.20 / 0.18 に減る（間を置かなくなる）。
- `controlled` は −4.4 Hz で p = 0.048 だが **1/5**。**p だけで段に数えない**
  （台本で最もよく使う語の 1 つなので、差があるとは書かない）。
- 抑揚（`f0_range_st`）は 12 語とも 7.7〜8.3 半音で動かない。**「感情のこもりかた」は
  抑揚には出ない。**

## 何が言えるか

- **delivery は 3 段：真ん中 8 語・上 2 語（aggressive / desperate）・
  下 2 語（cold / flat）。**
- 語の数（12）と、声に届く段の数（3〜4）が、まったく違う。
- delivery で差を作りたいなら `aggressive` / `desperate`（上）か `cold` / `flat`（下）。
  **真ん中の 8 語を書き分けても意味は出ない。** 上げ下げは `speed` と `pitch` で作る。

## 限界

- 1 行・1 人物・1 感情（joy）。emotion が変われば群の分かれかたも変わりうる。
- 「やさしさ」「明るさ」を測る計器は無い（f0・抑揚・長さ・energy・無音で見た）。
  抑揚が動かなかったことは、声質が同じという意味ではない。
- 動く 4 語の幅は 6.7〜18.4 Hz。**台本の `strong` の跳ね（+8.8〜+18.3 Hz）と同じ帯**で、
  これ単体で「強い演技」を作れる大きさではない。

## 測る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/acting-delivery
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/acting-delivery2
PYTHONPATH=. $PY bin/act_probe.py --tsv projects/longform/assets/acting-delivery/voice/*.wav \
  > projects/longform/acting-delivery/probe.tsv
PYTHONPATH=. $PY bin/act_probe.py --tsv projects/longform/assets/acting-delivery2/voice/*.wav \
  > projects/longform/acting-delivery2/probe.tsv
```
