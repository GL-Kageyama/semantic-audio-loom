# breathiness は、動くが小さい

`breathiness` は 4 語（none / slight / moderate / heavy）。**有声の割合と高域の比に、
単調だが小さい変化が出る。**

## 同じ行・同じ感情で、breathiness だけを振る

1 行「明日、また来るね。」・mashiro・joy・moderate・speed natural・delivery controlled・
seed 1〜5。`breathiness` を 4 語に振った 20 本（`script.yaml`）。

| breathiness | 有声の割合 | 高域の比 | energy (dB) |
| --- | --- | --- | --- |
| none | 0.276 | 0.0115 | −13.76 |
| slight | 0.272 | 0.0115 | −13.70 |
| moderate | 0.267 | 0.0126 | −13.86 |
| heavy | **0.263** | **0.0126** | −14.18 |

- **有声の割合は単調に下がる**（0.276 → 0.263）。moderate −0.009（0/5・p = 0.010）、
  heavy −0.013（0/5・p = 0.021）。**5 seed とも同じ向き**だが、幅は 1.3 ポイント。
- **高域の比（2.5〜8 kHz ÷ 100 Hz〜8 kHz・有声フレームだけ）は none・slight 0.0115 から
  moderate・heavy 0.0126 へ**、相対で +10%。段としては 2 段。
- energy は −0.1〜−0.4 dB（p ≥ 0.17）。**息は「小さくなる」ではなく「雑音が増える」。**
- f0 は 4 語とも 314〜316 Hz で動かない。

## 前の測定（beta 0.3・neutral・seed 3）は、差を見つけていない

`acting-breath/`（beta 0.3・neutral・seed 1〜3）では、有声の割合が
none 0.353/0.424/0.421・heavy 0.343/0.426/0.433 で、順序が無かった。

- **違う条件（beta・感情・seed 数）では、同じ欄が「出る／出ない」に分かれる。**
  効果が小さいので、**seed 3 本では検出できない**（5 本にして初めて 0/5 と p < 0.05 が出る）。
- ここで言えるのは「既定 0.7・joy では、単調で小さい変化がある」まで。
  **beta 0.3 でも同じ変化があるかは、測っていない。**

## 段の幅より大きいことが、seed 1 つで起きる

`acting-breath-s70/` は、芝居の 1 行（`s70`「……ばか。」・sadness / subtle / very_slow /
restrained）で `breathiness` だけを none と slight に振った 6 本。

| seed | none | slight | 差 |
| --- | --- | --- | --- |
| 1 | 329.7 Hz | **242.1 Hz** | **−87.6 Hz** |
| 2 | 235.9 Hz | 235.2 Hz | −0.7 Hz |
| 3 | 223.9 Hz | 225.2 Hz | +1.3 Hz |

- **seed 1 では語が 1 つ増えるだけで、丸ごと別の take になる**（f0 −87.6 Hz・長さ
  +0.03 秒）。seed 2・3 では 1 Hz しか動かない。**`breathiness` の効果は、平均で見ると
  小さいが、seed によっては欄を跨ぐ。**
- この効果は**上下に偏らない**（上がる側の例は未観測・n = 3）。上の表の 6 本では
  下がった 1 本と、動かない 2 本。**「息を足すと声が低くなる」とは言えない。**
- 出荷版の `s70` は、台本に `breathiness: slight` が入る前に作られていて、この seed 1 の
  329.7 Hz の側を焼いていた。作り直すと 242.1 Hz になり、**seed 2・3（236・224 Hz）と
  並ぶ**——つまり**古い take のほうが外れ値**だった。

## 何が言えるか

- `breathiness` は **段になるが、幅が 1.3 ポイント**。speed（1.80 倍）とは比べものにならない。
- 息を聴かせたいなら、**段を信じるより、`voice_fx` の帯域処理で作るほうが確実**
  （演劇のニジは電話の帯域を掛けている）。
- 「囁き」を演技で作ろうとしても、`volume` は 0 段（`acting-volume/`）、
  `breathiness` はこの幅。**囁きは、いまのところ欄では作れない。**

## 限界

- 1 行・1 人物・1 感情（joy）・beta 0.7。上のとおり beta 0.3 とは結果が違う。
- 高域の比はこの実験のために書いた計器（`acting/measure_breath.py`）。**耳との対応は
  確かめていない。** 有声フレームだけを見るので、前後の息づかいは入らない。
- 4 語のうち heavy が上限。heavy より上は無い。

## 測る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/acting-breath-070
PYTHONPATH=. $PY bin/act_probe.py --tsv projects/longform/assets/acting-breath-070/voice/*.wav \
  > projects/longform/acting-breath-070/probe.tsv
PYTHONPATH=. $PY projects/longform/acting/measure_breath.py \
  projects/longform/assets/acting-breath-070/voice/*.wav
```
