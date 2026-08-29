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
