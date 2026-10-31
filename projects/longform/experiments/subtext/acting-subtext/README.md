# subtext は、どこまで声に届くか

製品の売りは「台詞の裏の意味（subtext）を音に乗せる」。同じ 1 行
（「明日、また来るね。」・真白・neutral・moderate・natural・controlled・none・`beta` 0.7）で、
**subtext だけを 5 通りに振って**、どこまで声が動くかを 4 段で測った。

| 段 | 何を振ったか | 本数 | 結果 |
| --- | --- | --- | --- |
| 1. rule 解決 | subtext 5 通り × seed 5 | 25 | **音は同じ**（seed 3 だけノイズで 2 種） |
| 2. llm 解決 | subtext 5 通り × 1 | 5 | **5 通りの散文になる**（中身は欄ごとに違う） |
| 3. 固定した Spec × seed | 上の 5 つの Spec × seed 5 | 25 | **2 群**に割れる（−10 Hz・8 組すべて 5/5） |
| 4. 1 欄ずつ振る | intonation 2 × intensity 2 × seed 5 | 20 | **動くのは intensity だけ**（intonation は ±1 Hz） |

## 1. rule 解決では、音に載らない

`--resolve rule` は `subtext` を Spec の `subtext` 欄へ写す
（`semantic_audio_loom/engine/resolve.py:90`）。しかし Provider の散文を作る
`_spec_prompt`（`semantic_audio_loom/providers/tsukasa.py:199`）は **`subtext` を読まない**。
よって **Spec が同じなら音も同じ**になる。

25 本を 1 つのプロセスで焼いた md5（先頭 7 桁）:

| seed | none | return | never | angry | unspoken |
| --- | --- | --- | --- | --- | --- |
| 1 | `87dc440` | `87dc440` | `87dc440` | `87dc440` | `87dc440` |
| 2 | `2acef40` | `2acef40` | `2acef40` | `2acef40` | `2acef40` |
| 3 | `a72efea` | `6bd8633` | `a72efea` | `6bd8633` | `a72efea` |
| 4 | `f17a1f6` | `f17a1f6` | `f17a1f6` | `f17a1f6` | `f17a1f6` |
| 5 | `6bffd5e` | `6bffd5e` | `6bffd5e` | `6bffd5e` | `6bffd5e` |

- **seed 1・2・4・5 は 5 通りとも同じ音**。subtext は音に届いていない。
- **seed 3 だけ 2 種に割れた（3＋2）**。中身は subtext ではない。同じ台本を
  同じ順序でもう 2 回焼き直すと、**1 回目は 25 本とも元と一致**、**2 回目は
  seed 3 の return と angry の 2 本だけが、その回の none と同じファイルになった**
  （byte-identical）。差は最大 0.0093・RMS −54.2 dBFS、欄では `f0_end_st_s`
  にだけ出た（−3.60 / −3.85 半音・`probe.tsv`）。3 回の観測では、切り替わるのは
  毎回この 2 本（台本の 8 本目・18 本目）で、subtext の値ではなかった。
  同じ Spec の焼き直しで起きる件は [`../determinism/`](../../analysis/determinism)。
- seed の幅は f0 241.4〜326.0 Hz（**84.6 Hz**）。subtext の効果は 0 Hz（散文が
  同一）なので、この振れ幅は seed の側だけで決まっている。

## 2. llm 解決では、5 通りが 5 通りの散文になる

`--resolve llm` は subtext を具体的な演技指示へ変換する。1 回の解決の出力
（`llm-specs.json`）と、それが Provider の散文になったもの（`llm-prompts.tsv`）:

| subtext | `intonation` | `intensity` | Provider へ渡る散文（末尾だけ） |
| --- | --- | --- | --- |
| （なし） | neutral | 0.40 | … the feeling is faint, barely showing … |
| 本当は帰りたい | falling | 0.35 | … the feeling is faint … pitch falling at the end, trailing off. |
| もう来ないつもりだ | falling | 0.45 | … pitch falling at the end, trailing off. |
| 怒っている | flat | 0.50 | … flat and even at the end, no rise or fall. |
| 言いたいことがあるのに言えない | wavering | 0.40 | … the feeling is faint … voice wavering at the end, uncertain and hesitant. |

**5 通りが 5 通りの散文**になる。ただし LLM の出力は呼ぶたびに違う
（別の回では `neutral` / `falling` が 2 本ずつになった）。よって 3 段目からは
**1 回の解決を固定して**（`llm-specs.json`）、LLM の揺れと声の揺れを分ける。

`pauses`・`emphasis`・`breath` は LLM が書いてくるが、`_spec_prompt` は使わない
（Provider に構造化制御が無いため・同ファイルの註）。声に届くのは
**`intonation` と、`emotion.intensity` が 0.40 の境をまたぐかどうか**だけ。

## 3. 固定した Spec を seed で振ると、2 群に割れる

`run_llm_specs.py` で 5 つの Spec × seed 1〜5 = 25 本（`probe_llm.tsv`）。

| subtext | f0 中央値（seed 1〜5・Hz） | 平均 |
| --- | --- | --- |
| （なし） | 333.6 / 285.4 / 297.2 / 324.1 / 245.6 | 297.2 |
| 本当は帰りたい | 332.6 / 285.4 / 293.8 / 326.0 / 242.8 | 296.1 |
| 言いたいことがあるのに言えない | 333.6 / 285.4 / 297.2 / 326.0 / 248.5 | 298.1 |
| 怒っている | 323.2 / 274.9 / 285.4 / 313.0 / 238.6 | 287.0 |
| もう来ないつもりだ | 324.1 / 271.0 / 285.4 / 311.2 / 237.3 | 285.8 |

- **群の分かれ目は `intensity` 0.40 の境**（「the feeling is faint」の句が付くか）。
  付く 3 本（297.2 / 296.1 / 298.1）と付かない 2 本（287.0 / 285.8）。
- 群をまたぐ **6 組はすべて 5/5・−9.1〜−12.3 Hz**。
- **同じ群の中は 2.1 Hz 以下**（none − return +1.06・3/5、none − unspoken −0.96・0/5。
  向きが揃う組と揃わない組が混ざる）。**`intonation` が違っても声は変わらない**——
  それは 4 段目で 1 欄ずつ振って確かめる。

## 4. 1 欄ずつ振ると、動くのは intensity だけ

`run_knobs.py` で、`intonation`（neutral / wavering）と `emotion.intensity`
（0.5 = 句なし / 0.4 = 「faint」の句）だけを直交させて 4 通り × seed 5
（`probe_knobs.tsv`）。

| 比べたもの | f0 の差（平均） | 向きが揃った seed |
| --- | --- | --- |
| `intonation` wavering − neutral（intensity 0.5） | **+1.10 Hz** | 2/5 |
| `intonation` wavering − neutral（intensity 0.4） | **+0.96 Hz** | 2/5 |
| `intensity` 0.4 − 0.5（neutral） | **+6.92 Hz** | **5/5** |
| `intensity` 0.4 − 0.5（wavering） | **+6.78 Hz** | **5/5** |

- **`intonation` 語は実質 0**（3 本は f0 が同じ値・差は 0.0 Hz）。
  語尾の傾き（`f0_end_st_s`）にも揃った効果は出ない（+1.99 半音・3/5・
  1 本が +9.27 で平均を引っぱる。中央値 +0.47）。
- **動くのは `intensity` が 0.40 の境をまたぐとき**（+6.9 Hz・両方の設定で 5/5）。

## 何が言えるか

- **subtext それ自体は音に乗らない**（rule では経路が無い）。
- **llm 解決は subtext を散文へ変える**が、声を動かすのはそのうち
  **`intensity` が閾値をまたいだとき**だけ。`intonation` の語は散文を変えても
  声を変えない（このモデルでは語尾の傾きが言葉に従わない。
  `../acting-inton-070/` と同じ結論）。
- **「subtext を具体的な抑揚指示へ変換して初めて乗る」は、変換までは正しく、
  その先（抑揚語 → 声）がこのモデルでは効かない。** 効くのは強度の段だけ。

## 測る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python

# 1. rule 解決の 25 本（build_voice.py は rule 固定）
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/experiments/subtext/acting-subtext

# 2. llm 解決を 1 回だけ走らせて Spec を固定する（LLM の鍵が要る）
#    → llm-specs.json

# 3. 固定した Spec で焼く
PYTHONPATH=. $PY projects/longform/experiments/subtext/acting-subtext/run_llm_specs.py
PYTHONPATH=. $PY projects/longform/experiments/subtext/acting-subtext/run_knobs.py

# 4. 測る
PYTHONPATH=. $PY bin/act_probe.py --tsv projects/longform/assets/acting-subtext/voice/*.wav
```

素材は `projects/longform/assets/acting-subtext*/voice/`（追わない・焼き直せる）。
