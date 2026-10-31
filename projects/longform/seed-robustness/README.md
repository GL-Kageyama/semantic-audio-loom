# seed-robustness — 作品の段の数は seed で動くか

床（`beta` 0.0）の演劇「午前二時の電話」を、**cue の `seed` だけ** 1 / 2 / 3 に変えて
3 本作った。台詞・演技・間・効果音・帯域は同じ。作品の段で出した数
（感情 8 種の平均 f0 の幅・二人の高さの差・抑揚・間）が seed に依るかを見る。

| seed | 感情 8 種の平均 f0 の幅 | 二人の差（真白 − ニジ） | 抑揚（8 感情平均） | 間 | 声の合計 | 完成の尺 | 門 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | 79.1 Hz | +0.06 Hz | 7.40 半音 | 0.136 | 271.6 秒 | 339.1 秒 | 合格 |
| 2 | 66.2 Hz | +0.66 Hz | 7.46 半音 | 0.136 | 271.6 秒 | 339.0 秒 | 合格 |
| 3 | 70.6 Hz | +1.07 Hz | 7.45 半音 | 0.137 | 271.6 秒 | 339.1 秒 | 合格 |

## 何が分かったか

- **構造は seed に依らない。** 声の合計は 3 本とも **271.6 秒**（0.1 秒以内）、間は
  0.136 / 0.136 / 0.137、抑揚は 7.40 / 7.46 / 7.45。キューごとの f0 の相関は
  seed 1↔2 で **0.979**、1↔3 で **0.989**。**演技の設計は seed を替えても保たれる。**
- **二人の高さの差は、どの seed でも ~0。** +0.06 / +0.66 / +1.07 Hz。参照どうしは
  25 Hz 離れているので、**「床は二人の高さを同じにする」は seed に依らない**。
- **感情の幅だけが動く。** 79.1 / 66.2 / 70.6 Hz。差を作っているのは **fear**
  （351.8 / 338.9 / 343.4 Hz）と anger（293.4 / 288.4 / 292.7）。高い台詞の seed の
  揺れがそのまま幅になる。**79.1 は 1 つの seed の値で、3 seed の幅は 66〜79 Hz。**
- **順位は動かない。** 8 感情を平均 f0 の高い順に並べると 3 本とも同じ
  （fear > joy > anxiety > sadness > anger > guilt > loneliness > calm）。

## 測り方

- f0 は `semantic_audio_loom/skills/act_probe.py` の `f0_median_hz`（有声区間の中央値）。
- 二人の差は、キューごとの f0 から感情の平均を引いた残差を人物ごとに平均し、真白 − ニジ。
- 尺度 `seeds.tsv`（267 行＝89 キュー×3 seed）を `measure_seeds.py` が書く。

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/drama-beta00-s2
PYTHONPATH=. $PY projects/longform/assemble.py --dir projects/longform/drama-beta00-s2
PYTHONPATH=. $PY projects/longform/seed-robustness/measure_seeds.py
```

## 限界

- **3 seed だけ。** 幅のばらつきを言うには足りない。言えるのは「79.1 は固定値ではない」まで。
- 人が聴いて確かめた版ではない（自動の門と測定だけ）。
- ここで動かしたのは seed だけで、`alpha`・`beta`・台詞は固定。
