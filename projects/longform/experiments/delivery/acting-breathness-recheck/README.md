# 古い take に無かった `breathiness` は、音を変えていたか

`projects/longform/acting/` の 55 本は、`breathiness` が provider に届く前に焼かれている
（`params` の `prosody` に `breathiness` が無い。`check_script_sync.py` が 55/55 で鳴る）。
**そのせいで P2 の結論（枠外 10 種）が古い音の上に載っている疑い**を、6 種を作り直して
測った（`breathiness` を slight / heavy と書いた seed 1 の 7 本）。

| 種 | f0 (Hz) | 長さ (s) | 抑揚 (半音) | energy (dB) | 有声率 | 立ち上がり (ms) |
| --- | --- | --- | --- | --- | --- | --- |
| tere | +1.0 | +0.025 | 0.0 | +0.7 | −0.006 | +60 |
| akirame | −1.9 | −0.025 | −0.4 | +0.2 | +0.005 | +10 |
| sasayaki（heavy） | +3.8 | +0.05 | −0.6 | +0.5 | +0.006 | 0 |
| nakijwarai（heavy） | +2.1 | +0.10 | −0.2 | +0.1 | −0.002 | −10 |
| dokuhaku | +2.9 | −0.025 | +0.5 | +0.5 | −0.022 | −20 |
| hayakuchi | 0.0 | +0.025 | +0.7 | −0.5 | +0.010 | 0 |
| ma | +1.0 | 0.0 | +0.5 | −0.5 | −0.005 | 0 |

**どの差も、P2 の効果（f0 で +9〜+39 Hz・長さで 0.1〜1 秒）より 1 桁小さい。**
`breathiness` は平均ではほぼ効かない欄（`experiments/delivery/acting-breath-070/` で有声率 1.3 ポイント）
なので、**古い take のままの P2 の数値は、そのまま読める**。

- ⚠️ 確かめたのは **seed 1 の 7 本だけ**。`s70`（演劇）では breathiness が **seed 1 で
  take ごと入れ替えた**（−87.6 Hz）ので、**種によっては 1 本ずつで大きく動きうる**。
  P2 の各数値は 5 seed の中央値なので、1 seed の反転は中央値を壊さない。

## 測る

```bash
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/experiments/delivery/acting-breathness-recheck
PYTHONPATH=. $PY bin/act_probe.py --tsv projects/longform/assets/acting-breathness-recheck/voice/*.wav \
  > projects/longform/experiments/delivery/acting-breathness-recheck/probe.tsv
```
