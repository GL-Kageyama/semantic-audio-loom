# longform-acting-floor — 同じ一言を beta 0.7 / 0.3 / 0.0 で

同じ一言（「明日、また来るね。」）を、声の混ぜ方（`beta`）だけ変えて三つ並べた
71 秒の見本。語り手が札を読み、真白（`characters/mashiro.voice.yaml`）が毎回同じ台詞を
同じ seed 1 で言う。

- 前半 … `beta` 0.7（既定）
- 中盤 … `beta` 0.3
- 後半 … `beta` 0.0（床＝プロンプトの文面が prosody を全部決める段）

`beta` を下げるほど演技の差は開き、seed は効かなくなり、声は参照音声から離れる。
[longform-acting](../longform-acting/) の 0.7 対 0.3 に、床の 0.0 を足した版。

## 並び

| 秒 | 中身 |
| --- | --- |
| 1.4 | 導入（語り手） |
| 7.5 | 「まず、既定の混ぜ方。」 |
| 10.0 / 12.4 | 無表情 → 台詞（beta 0.7） |
| 15.0 / 17.0 | 喜び → 台詞 |
| 19.7 / 21.3 | 怒り → 台詞 |
| 25.2 | 「次は、0.3。」 |
| 27.8 / 30.2 | 無表情 → 台詞（beta 0.3） |
| 32.5 / 34.4 | 喜び → 台詞 |
| 37.1 / 38.7 | 怒り → 台詞 |
| 42.7 | 「最後は、床の 0.0。演技は、プロンプトの文面そのものになります。」 |
| 47.8 / 50.1 | 無表情 → 台詞（beta 0.0） |
| 52.4 / 54.3 | 喜び → 台詞 |
| 57.1 / 58.7 | 怒り → 台詞 |
| 62.7 | 結び（語り手） |

## 実測（この 1 本ずつ・seed 1）

| 台詞 | beta 0.7 | beta 0.3 | beta 0.0 |
| --- | --- | --- | --- |
| 無表情 | 326.0 Hz | 280.5 | **249.9** |
| 喜び | 351.4 | 339.4 | 341.4 |
| 怒り | 347.3 | 333.6 | 327.8 |
| 開き（喜び − 無表情） | +25.4 | +58.9 | **+91.5** |
| 台詞の長さ（無表情 / 怒り） | 2.85 / 2.95 秒 | 2.37 / 2.67 | 2.25 / 2.67 |

- 0.7 は三つとも 326〜351 Hz に集まる。**差は 21〜25 Hz。**
- 0.3 は無表情が下がり、差が 53〜59 Hz に開く。
- 0.0 は無表情が 250 Hz まで下がり、差が 78〜92 Hz。**台詞も短くなる**（語りが詰まる）。
- 5 seed の中央値・参照音声との包絡の距離・seed の揺れは
  [projects/longform/REPORT.md](../../projects/longform/REPORT.md) の「beta をさらに下げる」を見る。

## 作る

```zsh
PY=/Users/user/sonic-loom-spike/venv_tsukasa/bin/python
PYTHONPATH=. $PY projects/longform/explainer/build_voice.py --dir projects/longform/acting-floor
PYTHONPATH=. $PY projects/longform/assemble.py --dir projects/longform/acting-floor
ffmpeg -i projects/longform/assets/acting-floor/renders/acting-floor.wav -b:a 192k \
  examples/longform-acting-floor/acting-floor.mp3
```

## 限界

- **人が聴いて確かめた版ではない。** 自動の門だけを通した（ピーク −0.4 dBFS・
  クリップ 0・声の外の立ち上がり 0）。
- 尺 71 秒なので、5 分の門（`check_render.py`）は未達と出る。見本なので意図どおり。
- 台詞はすべて seed 1。**同じ条件でも作り直すと最後のビットは変わる**
  （差は RMS 0.0005〜0.0007 程度）。
