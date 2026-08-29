# mashiro-night — サンプル生成

キャラ（真白）＋演技（`anxious-night-call`）＋台詞「……まだ、起きてる？」から生成した音声の例。
このエンジンの差別化点である **subtext（台詞の裏の意味）** が反映された例：

| 入力 | 値 |
| --- | --- |
| キャラ | `mashiro`（`characters/mashiro.voice.yaml`・参照音声 `female_young_p308`） |
| 演技 | `anxious-night-call`（`performances/anxious-night-call.direction.yaml`） |
| 台詞 | ……まだ、起きてる？ |
| subtext | 返事が怖いが、繋がりを求めてしまう。 |
| seed | 462990461 |

- `mashiro_night.wav` … 生成された音声（24kHz・mono）
- `mashiro_night.params.yaml` … 保存済み Performance Spec（再生成の入力）

## 再生成

```bash
# 保存済み Spec を再利用（LLM は呼ばない・Tsukasa が必要）
bin/regenerate.py examples/mashiro-night/mashiro_night.params.yaml --out-dir /tmp/regen

# ゼロから同じ指定で生成
bin/generate.py --character mashiro --performance anxious-night-call \
    --project demo --scene night \
    --line "……まだ、起きてる？" --name mashiro_night --seed 462990461
```
