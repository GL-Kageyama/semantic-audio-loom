# shout は、大きくなかった

`experiments/delivery/acting-volume/` は whisper / quiet / normal / loud の 4 語を測った。残る `shout` を
同じ条件（「明日、また来るね。」・mashiro・joy・moderate・natural・gentle・seed 1〜5）で
足した 5 本。**5 語を並べた表と結論は `experiments/delivery/acting-volume/README.md`。**

## normal との対応のある差（seed 1〜5）

| 測ったもの | shout − normal | 同じ向き | p |
| --- | --- | --- | --- |
| f0 中央値 | **+9.6 Hz** | **5/5** | **0.0060** |
| 長さ | **+0.13 秒** | **5/5** | **0.0038** |
| 無音の割合 | +0.026 | 5/5 | 0.013 |
| **energy 中央値** | **−0.6 dB** | **0/5** | 0.075 |
| **rms** | **−0.76 dB** | **0/5** | — |
| 抑揚（`f0_range_st`） | +0.06 半音 | 3/5 | 0.63 |

- **叫ぶと、高く長くなる。だが大きくならない**（energy は 0.6 dB 下がる）。
  whisper（−13.54 dB）より shout（−14.36 dB）のほうが小さい。
- 5 本とも peak は 0.9500。**大きさは Normalize で揃い、聴こえる声量は
  `assemble.py` の `VOLUME_GAIN`（shout は +6 dB）が作る。**

## 測る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/experiments/delivery/acting-volume-shout
PYTHONPATH=. $PY bin/act_probe.py --tsv projects/longform/assets/acting-volume-shout/voice/*.wav \
  > projects/longform/experiments/delivery/acting-volume-shout/probe.tsv
PYTHONPATH=. $PY projects/longform/check_script_sync.py --dir projects/longform/experiments/delivery/acting-volume-shout
```
