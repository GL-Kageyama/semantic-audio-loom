# 聞き比べ — 裏の意味だけを替える（**同じ音が五回**）

`projects/longform/experiments/demos/subtext-demo/` の 42.2 秒。語り手が裏の意味を読み、真白が同じ台詞
（「明日、また来るね。」）・同じ演技・同じ seed 4 を 5 通りで言う。

| 時刻 | 裏の意味 | 真白の声 |
| --- | --- | --- |
| 0:01.4 | 導入「同じ台詞を、裏の意味だけ変えて、五回いいます」 | — |
| 0:06.7 | 裏の意味なし | **0:09.0** |
| 0:12.3 | 本当は、帰りたい | **0:14.9**（同じ音） |
| 0:18.2 | もう、来ないつもりだ | **0:20.8**（同じ音） |
| 0:24.1 | 怒っている | **0:26.1**（同じ音） |
| 0:29.4 | 言いたいことがあるのに、言えない | **0:32.9**（同じ音） |
| 0:36.6 | 結び「五つとも、同じ音になりました。裏の意味は、声に届いていません」 | — |

## 聴きどころ

- **5 本はバイトまで同じ**（`md5 f17a1f6` が 5 本）。**聞き分けようがない。**
- これは既定の解決（`--resolve rule`）の話。rule は `subtext` を Spec へ写すが、
  声を作る散文がその欄を読まない（`docs/resolve.md`「どこまで声に届くか」）。
- `--resolve llm` で裏の意味を散文へ変えると音は変わるが、**効くのは強度の段だけ**で、
  抑揚の語（flat / falling / wavering）は声を動かさない
  （`projects/longform/experiments/subtext/acting-subtext/`：+1.0 Hz・2/5）。
- 測った数：`experiments/subtext/acting-subtext/probe.tsv`（25 本）・`probe_llm.tsv`（25 本）・
  `probe_knobs.tsv`（20 本）。

## 作る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/experiments/demos/subtext-demo
PYTHONPATH=. $PY projects/longform/assemble.py --dir projects/longform/experiments/demos/subtext-demo
PYTHONPATH=. $PY projects/longform/check_render.py \
  projects/longform/assets/subtext-demo/renders/subtext-demo.wav --mix projects/longform/experiments/demos/subtext-demo/mix.yaml
PYTHONPATH=. $PY projects/longform/deliver.py \
  projects/longform/assets/subtext-demo/renders/subtext-demo.wav \
  examples/longform/subtext/subtext-demo.mp3 --gain -0.35
```

配布 mp3 は −15.62 LUFS・トゥルーピーク −1.01 dBTP・LRA 4.70 LU（`check_loudness.py` 合格）。
