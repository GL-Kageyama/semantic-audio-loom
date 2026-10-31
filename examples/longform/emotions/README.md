# 聞き比べ — 感情を 11 語ぜんぶ並べると、どこまで違って聞こえるか

`projects/longform/experiments/demos/emotion-demo/` の 75.4 秒。語り手が感情の名前を読み、真白が同じ台詞
（「明日、また来るね。」）・同じ seed（4）を、11 の感情で言う。並びは実測した f0 の
**5 seed の平均**の低い順。

| 時刻 | 何が鳴るか | f0（seed 4 のこの 1 本） |
| --- | --- | --- |
| 0:01.4 | 導入「同じ台詞を、十一の感情で言います。声の高さの、低い順に」 | — |
| 0:10.2 | **中立** | 313.0 Hz |
| 0:15.8 | **悲しみ** | 320.4 Hz |
| 0:22.2 | **罪悪感** | 316.7 Hz |
| 0:27.4 | **孤独** | 323.2 Hz |
| 0:32.6 | **穏やか** | 324.1 Hz |
| 0:37.9 | **不安** | 335.5 Hz |
| 0:43.9 | **自信** | 333.6 Hz |
| 0:49.8 | **興奮** | 335.5 Hz |
| 0:54.9 | **怒り** | 341.4 Hz |
| 1:00.3 | **喜び** | 343.4 Hz |
| 1:05.4 | **恐怖** | 341.4 Hz |
| 1:09.0 | 結び「隣り合う感情は、同じ声に聞こえます。離れた感情だけが、違って聞こえます」 | — |

## 聴きどころ

- **隣どうしは、同じ声に聞こえる。** 中立 313.0 と罪悪感 316.7 は 3.7 Hz。
  罪悪感 316.7 と悲しみ 320.4 は 3.7 Hz。**11 語は 11 段ではない。**
- **離れた 2 語だけが違う。** 中立 313.0 → 喜び 343.4 は 30.4 Hz。
  0:10.2 と 1:00.3 を続けて聞くと、同じ台詞とは思えない。
- **長さはほとんど動かない**（3.22〜3.62 秒）。**感情の差は、主に高さ。
  ただし 1 本ずつ聞いて名前を当てるのは無理**——seed を替えると、この 30 Hz より
  大きく動く（`projects/longform/experiments/basics/acting-emotion-ladder/`）。

## 11 本の実測（`act_probe`）

| emotion | f0 (Hz) | 長さ (s) | 抑揚 (半音) |
| --- | --- | --- | --- |
| neutral | 313.0 | 3.30 | 8.1 |
| sadness | 320.4 | 3.57 | 7.8 |
| guilt | 316.7 | 3.62 | 7.9 |
| loneliness | 323.2 | 3.37 | 8.1 |
| calm | 324.1 | 3.55 | 7.9 |
| anxiety | 335.5 | 3.50 | 8.3 |
| confidence | 333.6 | 3.55 | 8.2 |
| excitement | 335.5 | 3.50 | 8.2 |
| anger | 341.4 | 3.50 | 8.5 |
| joy | 343.4 | 3.32 | 8.3 |
| fear | 341.4 | 3.22 | 9.3 |

- ⚠️ **並びは 5 seed の平均の順**（neutral 290.3 … fear 315.8）。**この 1 本（seed 4）では
  3 組が入れ替わる**：sadness と guilt、anxiety と confidence、joy と fear。
  差は 2〜4 Hz なので、**聞いても順番は分からない**——それがこの見本の言いたいこと。

## 作る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/experiments/demos/emotion-demo
PYTHONPATH=. $PY projects/longform/assemble.py --dir projects/longform/experiments/demos/emotion-demo
PYTHONPATH=. $PY projects/longform/check_render.py \
  projects/longform/assets/emotion-demo/renders/emotion-demo.wav \
  --mix projects/longform/experiments/demos/emotion-demo/mix.yaml
PYTHONPATH=. $PY projects/longform/deliver.py \
  projects/longform/assets/emotion-demo/renders/emotion-demo.wav \
  examples/longform/emotions/emotion-demo.mp3 --gain -0.35
```

配布 mp3 は −15.64 LUFS・トゥルーピーク −1.01 dBTP・LRA 4.10 LU（`check_loudness.py` 合格）。
