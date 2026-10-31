# pitch の 6 語：下がる語は 3 語、上がる語は 0 語

`pitch` は 6 語（very_low / low / slightly_low / natural / slightly_high / high）。
これまでは low / natural / high の 3 語だけを測っていた。**6 語 × seed 10 本を、
1 つの条件で並べた**（同じ行・joy・moderate・speed natural・`delivery` controlled・
breathiness none・beta 0.7・60 本）。

| pitch | f0 (Hz) | natural との差 | 同符号 | p |
| --- | --- | --- | --- | --- |
| **very_low** | **299.0** | **−16.5 Hz** | 0/10 | 0.0012 |
| **low** | **302.0** | **−13.5 Hz** | 1/10 | 0.00018 |
| **slightly_low** | **309.7** | **−5.8 Hz** | 0/10 | 9.1e−07 |
| natural | 315.5 | — | — | — |
| slightly_high | 312.9 | **−2.6 Hz** | 0/10 | 0.00022 |
| high | 315.4 | −0.1 Hz | 1/10 | 0.87 |

## 段は 3 つ、すべて下

- **`very_low` と `low` は、同じ段**（very_low − low = −3.0 Hz・3/10・p = 0.19）。
- **`low` → `slightly_low` は開く**（−7.7 Hz・1/10・p = 0.0036）。
- **上がる語は 1 つも無い。** `high` は natural と同じ（−0.1 Hz）。`slightly_high` は
  **わずかに下がる**（−2.6 Hz・0/10・p = 0.0002）——**向きが名前と逆**。
- 全体の幅は **16.5 Hz**（very_low 299.0 ↔ natural 315.5）。**この欄だけで声を高くする
  ことはできない。**

## 長さと抑揚は動かない

- 長さは 3.08〜3.26 秒（slightly_low 3.10 / natural 3.09 / high 3.11）。**段にならない。**
- 抑揚は 7.35〜7.88 半音。**低い語ほどわずかに狭い**（very_low 7.37 / natural 7.82 / high 7.88）。
  −0.45 半音で、**seed の散らばり（標準偏差 0.80〜1.05 半音・1 本で 3 半音の幅）に埋もれる。**

## 上側は、状態で変わる

| 条件 | high − natural | low − natural |
| --- | --- | --- |
| joy・moderate・controlled（本実験・seed 10） | **−0.1 Hz** | −13.5 Hz |
| joy・moderate・gentle（`acting-knob-stack-pitch/`・seed 5） | +2.9 Hz | −7.8 Hz |
| neutral の声（REPORT「欄ごとの段」・3 語） | **+18.8 Hz** | — |

- **`high` の効きは 0〜+19 Hz のあいだで動く。** `low` の効きは −8〜−14 Hz に収まる。
- 読むとき：**`pitch` で低くするのは当てにできる。高くするのは当てにできない**
  （上げたいなら `speed` の端・+15〜17 Hz、ただし長い行では効かない）。

## 限界

- 1 行・1 人物（mashiro）・1 感情（joy）。句読点のない 1 文。
- 長さ・抑揚・f0 中央値だけ。声質・息・語尾は見ていない。
- 「neutral の声で high +18.8」は別の実験（条件が違う）から持ってきた数。

## 測る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/acting-pitch-ladder
PYTHONPATH=. $PY bin/act_probe.py --tsv projects/longform/assets/acting-pitch-ladder/voice/*.wav \
  > projects/longform/acting-pitch-ladder/probe.tsv
PYTHONPATH=. $PY projects/longform/check_script_sync.py --dir projects/longform/acting-pitch-ladder
```
