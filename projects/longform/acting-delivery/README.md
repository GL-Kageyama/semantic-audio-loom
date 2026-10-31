# delivery の 11 語は、2 つの群に落ちる

`delivery` は語が一番多い欄（11 語）。台本はこれもよく書く（演劇 89 本のうち
gentle 30・cheerful 14・hesitant 13・flat 9・restrained 9・cold 6・desperate 5・
aggressive 2）。**振っても、声が動くのは「平ら・冷たい」側だけ。**

## 同じ行・同じ感情で、delivery だけを振る

1 行「明日、また来るね。」・mashiro・joy・moderate・volume normal・speed natural・
seed 1〜5。`delivery` を 6 語に振った 30 本（`script.yaml`。全部は試していない）。

| delivery | f0 (Hz) | 抑揚 (半音) | 長さ (s) | energy (dB) | 無音の割合 |
| --- | --- | --- | --- | --- | --- |
| gentle | 318.6 | 7.94 | 3.16 | −14.08 | 0.28 |
| cheerful | 317.5 | 7.82 | 3.14 | −14.14 | 0.27 |
| hesitant | 317.1 | 7.96 | 3.15 | −14.18 | 0.27 |
| restrained | 316.7 | 7.92 | 3.14 | −13.88 | 0.27 |
| cold | 309.2 | 8.30 | 2.91 | −13.38 | 0.20 |
| flat | **300.2** | 7.82 | 2.87 | −13.34 | 0.18 |

gentle との対応のある差（seed 5 本）:

| delivery | f0 | 同符号 | p |
| --- | --- | --- | --- |
| cheerful | −1.1 Hz | 1/5 | 0.39 |
| hesitant | −1.5 Hz | 1/5 | 0.27 |
| restrained | −1.9 Hz | 1/5 | 0.17 |
| cold | **−9.4 Hz** | 1/5 | 0.033 |
| flat | **−18.4 Hz** | 0/5 | 0.013 |

- **gentle / cheerful / hesitant / restrained の 4 語は、2 Hz 以内で見分けがつかない。**
- **cold と flat だけ下がる**（−9.4・−18.4 Hz）。長さも縮む（−0.25・−0.29 秒・0/5）。
  無音の割合も 0.27 → 0.20 / 0.18 に減る（間を置かなくなる）。
- 抑揚（`f0_range_st`）は 6 語とも 7.8〜8.3 半音で動かない。**「感情のこもりかた」は
  抑揚には出ない。**

## 何が言えるか

- **delivery は「普通」と「無感情」の 2 群。** 「やさしく」「明るく」「ためらい」
  「抑えて」は、同じ声になる。
- 語の数（11）と、声に届く段の数（2）が、まったく違う。
- delivery で差を作りたいなら、`cold` / `flat` を使うか、**別の欄（speed・pitch・
  beta）で作る**。

## 限界

- 6 語だけ試した（desperate・aggressive・intimate・suppressed・subtle は未測）。
- 1 行・1 人物・1 感情（joy）。emotion が変われば群の分かれかたも変わりうる。
- 「やさしさ」「明るさ」を測る計器は無い（f0・抑揚・長さ・energy・無音で見た）。
  抑揚が動かなかったことは、声質が同じという意味ではない。

## 測る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/acting-delivery
PYTHONPATH=. $PY bin/act_probe.py --tsv projects/longform/assets/acting-delivery/voice/*.wav \
  > projects/longform/acting-delivery/probe.tsv
```
