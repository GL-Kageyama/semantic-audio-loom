# 途中の句点 1 つで、`！` の効きは半分以下になる

`experiments/punctuation/acting-punctuation-long/` では、24 文字の同じ行で途中の句点を読点に替えると
`！` の効きが +13.2 → +22.0 Hz に戻った。長さが同じでも効いたので、原因は
途中の句点らしい。**行を短くしたまま**それを直接見る。

「明日。また来るね」の末尾だけを `。` / `！` に振る（2 通り × seed 5 = 10 本）。
対照は同じ話者の「明日、また来るね」（`experiments/punctuation/acting-punctuation/`。途中は読点・9 文字）。
Spec は共通（`experiments/subtext/acting-subtext/llm-specs.json` の none＝neutral・0.5・controlled）。

    PYTHONPATH=. $PY projects/longform/experiments/punctuation/acting-punctuation-period/run.py
    PYTHONPATH=. $PY bin/act_probe.py --tsv …/voice/*.wav > probe.tsv

## 測った値

| 文末 | f0 | 長さ |
| --- | --- | --- |
| `。` | 297.5 Hz | 3.26 s |
| `！` | 312.1 Hz | 3.11 s |

`。` との差（seed ごとの対の平均・5 本）:

| 文末 | f0 の差 | 長さの差 |
| --- | --- | --- |
| `！` | **+14.6 Hz（5/5・+6.8〜+28.0）** | **−0.15 s（0/5）** |

## 読み方

- **文字数は同じ 9 文字。違うのは途中が読点か句点かだけ。**
  `、` の行は +39.3 Hz、`。` の行は **+14.6 Hz**。**途中で文が切れると、
  最後の `！` の効きは半分以下になる。**
- **途中に句点がある行は、長さが違っても効きが揃う**——9 文字 +14.6・
  24 文字 +15.0 Hz。**句点があるかどうかが先で、長さは後。**
- 長さは 5 本とも縮む（−0.15 s）。他の行と同じ向き。
- 途中の句点そのものの効果（f0 の基準線が `。` の行で 297.5・`、` の行で 297.2 Hz）は
  1 文字の違いで、seed の揺れ（84.6〜92.7 Hz）の中にある。**見えているのは
  末尾の `！` の効きの差だけ**で、途中の句点が基準線を動かすとは言えない。
