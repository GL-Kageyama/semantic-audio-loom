# 声量（loudness）の三層分業

「声を大きくしたい」を単一のボリュームで済ませない。

| レイヤ | フィールド | 何を表すか |
| --- | --- | --- |
| Direction（意図） | `performance.volume` | 演出上の「ささやく／叫ぶ」 |
| Interpretation（実現） | `loudness.effort` | 声帯の張り・努力（張り） |
| Mixing（量） | ピーク正規化 | 再生音量の統一（張りには非関与） |

## 解決の流れ

1. Direction の `volume`（whisper / quiet / normal / loud / shout）を Resolve が `loudness.effort`（relaxed / normal / projected / strained）へ解決。
2. Provider（Tsukasa）が effort を声量文言へ変換（relaxed→"quietly"、strained→"shouting, at full volume"）。
3. Mixing は `normalize.py` のピーク正規化（0.95）のみ。

## 重要な点

**ゲインを上げても「張り」は増えない。**

M0 実測：angry rms 0.086 vs sad 0.055 は音量でなく演技の差。ピーク正規化は再生音量を揃えるだけで、声帯の張り（演技）には関与しない。

**5 語を振っても、声の energy は動かない。** 同じ行・同じ seed で whisper / quiet /
normal / loud / shout を振ると、whisper と loud の差は energy 0.08 dB・rms 0.02 dB。
`shout` だけは f0 +9.6 Hz・長さ +0.13 秒を動かすが、**energy は 0.6 dB 下がる**
（`projects/longform/experiments/delivery/acting-volume/`）。**聴き手が聴く声量は `assemble.py` の
`VOLUME_GAIN`（−10 / −5 / 0 / +3 / +6 dB）が決めている。**

## 配布の音量と、圧縮を掛けない理由

`deliver.py` は**直線のゲインだけ**を掛け、トゥルーピークを −1 dBTP へ収める。
ピークに当たっている素材は −16 LUFS に届かないが、**圧縮は掛けない**——山と谷の差
（息づかい・間際の子音・長い間）がそのまま残るほうを採る。

- 掛ける方法（`loudnorm` の 2 パス・`I=-16:TP=-1.0:LRA=11`）と、その代償の測り方は
  [`projects/longform/experiments/analysis/loudness-trial/`](../projects/longform/experiments/analysis/loudness-trial) に残してある。
- 掛けると門には入るが、**谷が +2〜+7 dB 持ち上がり、幅（LRA）が 1.1〜5.1 LU 縮む**。
  元の谷は戻せない。**同じ原因が別の作品で出たとき**だけ、この手順を使う。
- 届かなかった見本は「未達」として記録する（音を削って目安に合わせない）。
