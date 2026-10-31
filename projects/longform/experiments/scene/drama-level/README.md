# drama-level — 演劇の三つの版をキューごとに測った記録

同じ脚本・同じ seed・同じ間で、混ぜ方（`beta`）だけを 0.7 / 0.3 / 0.0 に変えた
「午前二時の電話」の声を、キューごとに `bin/act_probe.py` と同じ指標で測ったもの。

| ファイル | 中身 |
| --- | --- |
| `levels.tsv` | 267 行（89 キュー × 3 版）。`beta` 列が版 |
| `measure_levels.py` | `levels.tsv` を作り直す道具 |

列：`beta` / `name` / `character` / `emotion` / `intensity` / `volume` / `speed` /
`delivery` / `duration` / `f0_median_hz`（有声区間の中央値）/ `f0_range_st`（p5–p95 の半音幅）/
`rate_mora_s` / `pause_ratio` / `energy_median_db` / `voiced_fraction`。
指標の定義は `semantic_audio_loom/skills/act_probe.py` の冒頭。

```bash
PYTHONPATH=. /Users/user/sonic-loom-spike/venv_tsukasa/bin/python \
  projects/longform/experiments/scene/drama-level/measure_levels.py
```

声の WAV は `assets/drama{,-beta03,-beta00}/voice/` にあり、追わない（同じ設定で作り直せる）。
読み取りと結論は `../REPORT.md` の「作品の段で、床は何を広げ、何を平らにするか」。
