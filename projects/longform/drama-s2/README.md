# drama-s2 — 既定（beta 0.7）の演劇を seed 2 で作ったもの

`drama/script.yaml` の `seed` を 1 → 2 にしただけ。**測定用**で、組み上げていない
（`assets/drama-s2/voice/` の 89 本だけ）。

作品の前半・中盤・後半で二人の高さがどう動くかを、seed 1（`drama-level/levels.tsv`）と
突き合わせるために作った。測り方は
[`../seed-robustness/measure_drift.py`](../seed-robustness/measure_drift.py)。

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/drama-s2
PYTHONPATH=. $PY projects/longform/seed-robustness/measure_drift.py
```
