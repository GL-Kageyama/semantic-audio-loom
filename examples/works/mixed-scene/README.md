# 統合の例 — 声・bgm・sfx を 1 本にする

3 層を重ねた 14 秒の場面。生成は各段の CLI、重ねるのは `bin/mix.py`。

| 層 | ファイル | 何 | 置き場所 |
| --- | --- | --- | --- |
| bed | `b-ambient.wav` | musicgen の pad（9.94 秒） | 0.0 秒・−18 dB |
| voice | `v-calm.wav` | 「窓の外、雨だよ。」（3.4 秒） | 1.4 秒 |
| voice | `v-anxious.wav` | 「……まだ、起きてる？」（2.5 秒） | 4.0 秒 |
| voice | `v-tired.wav` | 「そっか。じゃあ、もう寝る。」（3.9 秒） | 6.4 秒 |
| hit | `../sound-samples/sfx-door-slam.wav` | 木の戸が閉まる | 0.05 秒・−6 dB |
| hit | `../sound-samples/sfx-switch-click.wav` | スイッチ | 1.2 秒・−8 dB |
| hit | `../sound-samples/sfx-gravel-steps.wav` | 砂利の足音 | 2.4 秒・−14 dB |
| hit | `../sound-samples/sfx-glass-break.wav` | グラスが割れる | 5.6 秒・−10 dB |
| hit | `../sound-samples/sfx-thunder-far.wav` | 遠雷 | 8.0 秒・−12 dB |

sfx は [../sound-samples/](../sound-samples/) の実物をそのまま指す（同じ WAV を二重に置かない）。

`mix.yaml` がそのまま置き場所の宣言。生成済みの WAV を束ね直すだけなので 1 秒で終わる。

```bash
bin/mix.py --file examples/mixed-scene/mix.yaml --out-dir /tmp/out --json
```

## 実測（`bin/probe.py` と、ステムを重ね直した比較）

- 本編：14.0 秒・2ch（ステレオ）・peak 0.95・RMS −17.8 dBFS・無音率 21.8%・起伏 24.1 dB・注意なし。
- **ducking は声の間だけ効いている**：声の鳴っている標本に限ると bed は
  8.0 / 8.3 / 7.8 dB 沈み（3 つの声）、声の無い区間は 0.0 dB（素通し）。
  沈める量は声の 5ms 包絡が −30 dBFS を超えた分で、10 dB で頭打ち。
- 声は埋もれない：声の区間のミックス RMS は声そのものの RMS とほぼ同じ
  （声 −16.4 / −15.3 / −17.1 dB に対しミックス −15.0 / −15.0 / −17.1 dB）。声が最上段にある。
- チャンネルはステムの最大に揃える。mono の声は両耳の真ん中（複製）、ステレオの sfx は
  左右を保つ。この場面は bed と声が主なので中央が強く、側（L−R）/2 は全体 −50.6 dB・
  ガラスの割れる区間でも −43.8 dB と小さい——sfx の広がりは残っているが主役ではない。

## やっていないこと

- **パン（定位を動かす機能）は無い。** ステムの定位はそのまま通る（声は真ん中、
  sfx は生成物の左右）。「この音を右 30% へ」と置く指定はまだ無い。
- **LUFS マスター正規化は無い。** 天井（peak 0.95）だけを最後に一度掛ける。
- 声の尺は生成のまま。間（無音）を詰めたいときは `mix.yaml` の `start` を動かす。

## ライセンス

声（Tsukasa_Speech）と musicgen（CC-BY-NC 4.0）・stable_audio（Stability AI Community
License）の条件に従う。非商用のサンプル。
