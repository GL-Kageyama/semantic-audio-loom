# 長い台詞でも、速さは 5 段のまま

`speed` の 5 段は 3 秒の一言（「明日、また来るね。」）で測ってきた。台本の実際の行は
もっと長いので、**同じ助言が長い行にも効くか**を、芝居の 1 行
「最初に会ったとき。画面の向こうで、虹が揺れてた。」（24 文字・句点 2 つ・`drama` の
`s47`）で測った。5 語 × seed 5・25 本。joy・moderate・volume normal・delivery controlled
（`experiments/delivery/acting-longline/` と同じ行・同じ条件で、振る欄だけ speed に替えた）。

## 長さ（秒・seed 5 の平均）

| 速さ | 長い行 | 一言（`experiments/delivery/acting-speed/`） |
| --- | --- | --- |
| very_slow | 7.44 | 4.39 |
| slow | 5.93 | 3.59 |
| natural | 5.26 | 3.06 |
| fast | 4.92 | 2.84 |
| very_fast | **4.26** | 2.44 |
| 比（very_slow ÷ very_fast） | **1.75** | 1.80 |

| 段の間 | 長い行 | 一言 |
| --- | --- | --- |
| very_slow → slow | −1.51 s（5/5・p = 3.3e−07） | −0.80 s |
| slow → natural | −0.67 s（5/5・p = 6.2e−04） | −0.53 s |
| natural → fast | −0.34 s（5/5・p = 9.9e−05） | −0.22 s |
| fast → very_fast | −0.67 s（5/5・p = 5.2e−06） | −0.40 s |

## 何が言えるか

- **5 seed すべてで 5 語が単調（5/5）。** 比は 1.75 倍で、一言の 1.80 倍とほぼ同じ。
  **速さの段は、文字数で割り算しない**（長い行では秒の差は 1.7 倍に拡大するが、
  比は動かない）。台本を書くときは**比で読む**。
- **動くのは発話の側。** 無音の割合は 0.23〜0.28 で段に並ばない。
- **高さ・抑揚の幅・張りも動かない**（f0 285.2 / 280.1 / 282.9 / 279.3 / 284.5 Hz、
  抑揚 8.02 / 7.80 / 7.52 / 7.78 / 8.18 半音、energy −13.5〜−13.9 dB・どれも非単調）。
  **速さは「時間だけ」のノブ。**

## 限界

- **1 行・1 感情（joy）。** 感情を替えた速さは `experiments/delivery/acting-speed-emotions/`（短い行）で測った。
- 句点 2 つで間が入る行なので、`very_slow` の 7.44 秒には設計上の無音も含む。
- 長さの比は「この行の文字数と句読点」のもの。24 文字より短い行と長い行は未測
  （いま測ったのは 3 秒の一言と 5〜7 秒の行の 2 点）。

## 測る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/experiments/delivery/acting-speed-longline
PYTHONPATH=. $PY bin/act_probe.py --tsv projects/longform/assets/acting-speed-longline/voice/*.wav \
  > projects/longform/experiments/delivery/acting-speed-longline/probe.tsv
```
