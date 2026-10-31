# `breathiness: slight` ひとつで、take が変わる seed がある

`breathiness` の段の幅は小さい（`acting-breath-070/`・有声の割合 1.3 ポイント）。
だが**作品の 1 本では、語を 1 つ足しただけで f0 が 87.6 Hz 動いた**。それが本当に
`breathiness` のせいかを、欄だけを振って確かめた。

## 条件

芝居の `s70`（「……ばか。」・mashiro・sadness / subtle / volume quiet / very_slow /
delivery restrained・`pause_before` 無し）で、`breathiness` を none / slight、seed 1〜3。
6 本（`script.yaml`）。

| seed | none | slight | 差 |
| --- | --- | --- | --- |
| 1 | **329.7 Hz** / 2.123 秒 | **242.1 Hz** / 2.148 秒 | **−87.6 Hz** / +0.03 秒 |
| 2 | 235.9 Hz / 2.248 秒 | 235.2 Hz / 2.273 秒 | −0.7 Hz / +0.03 秒 |
| 3 | 223.9 Hz / 2.273 秒 | 225.2 Hz / 2.298 秒 | +1.3 Hz / +0.03 秒 |

- **seed 1 だけが丸ごと別の take になる。** seed 2・3 は 1 Hz しか動かない。
- **向きは一定でない**（3 seed のうち 1 本が下、2 本が動かない）。
  **「息を足すと低くなる」とは言えない。**
- 長さは 3 seed とも +0.03 秒で、**長さの側は動かない。**

## なぜ測ったか

出荷版の `s70` は、台本に `breathiness: slight` が入る**前**に作られていた
（`assets/drama/voice` の `created_at` が台本の更新より前）。台本どおりに作り直すと
f0 が 329.7 → 242.1 Hz に動いたので、**台本と音の食い違いが、この欄のせいかを確かめた**。

- 作り直した値（242.1）は seed 2・3（236・224）と並ぶ。**古い take のほうが外れ値**で、
  作り直しのほうが「同じ台詞の他の seed」に近い。
- 演劇の `s70` は `pause_before: 2.5` で置かれているため、この実験では間を 0 にして
  声だけを比べている。

## 限界

- **3 seed・1 行。** seed 1 の外れが再現するかは、別の行で確かめていない。
- 6 本とも beta 0.7・alpha 0.35。beta 0.3 では未測（`acting-breath/` は差を出していない）。
- 「別の take」と言っているのは f0 と長さの話。**耳で確かめてはいない。**

## 測る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/acting-breath-s70
PYTHONPATH=. $PY bin/act_probe.py --tsv projects/longform/assets/acting-breath-s70/voice/*.wav
```
