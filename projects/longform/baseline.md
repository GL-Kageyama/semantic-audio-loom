# 基準線 — examples/ の全 WAV（P0・2026-10-31）

`bin/probe.py --json` で測った。量（peak / RMS / クリップ）は**全チャンネル**で測る。
`burst_db` は 10ms 包絡の最大−中央値。`注意` は probe の flags（名前だけ）。

| ファイル | 長さ s | 標本化 Hz | ch | peak | RMS dB | 無音率 | burst dB | 重心 Hz | 注意 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `gozen-niji-ch01/gozen-niji-ch01.wav` | 18.82 | 24000 | 1 | 0.950 | -16.5 | 45.6% | 25.4 | 508 | — |
| `gozen-niji-katari-scenes/katari_ch01_body.wav` | 9.37 | 24000 | 1 | 0.950 | -14.9 | 34.4% | 17.7 | 438 | — |
| `gozen-niji-katari-scenes/katari_ch01_clock.wav` | 7.47 | 24000 | 1 | 0.950 | -15.3 | 38.1% | 15.4 | 407 | — |
| `gozen-niji-katari-scenes/katari_ch01_opening.wav` | 10.27 | 24000 | 1 | 0.950 | -14.7 | 33.8% | 15.1 | 461 | — |
| `gozen-niji-katari-scenes/katari_ch01_refrain.wav` | 9.90 | 24000 | 1 | 0.950 | -14.4 | 37.9% | 18.1 | 491 | — |
| `gozen-niji-katari-scenes/katari_ch12_ending.wav` | 9.97 | 24000 | 1 | 0.950 | -17.7 | 41.1% | 17.6 | 729 | — |
| `mashiro-night/mashiro_itterasshai.wav` | 3.50 | 24000 | 1 | 0.950 | -15.8 | 46.0% | 29.1 | 715 | — |
| `mashiro-scenes/mashiro_ch02.wav` | 1.90 | 24000 | 1 | 0.950 | -17.5 | 43.9% | 30.9 | 531 | — |
| `mashiro-scenes/mashiro_ch03.wav` | 0.67 | 24000 | 1 | 0.950 | -11.4 | 41.7% | 11.1 | 258 | bass_heavy |
| `mashiro-scenes/mashiro_ch05.wav` | 3.82 | 24000 | 1 | 0.950 | -14.8 | 33.1% | 16.0 | 684 | — |
| `mashiro-scenes/mashiro_ch11.wav` | 3.70 | 24000 | 1 | 0.950 | -14.6 | 39.7% | 16.2 | 740 | — |
| `mashiro-scenes/mashiro_ch12.wav` | 3.07 | 24000 | 1 | 0.950 | -16.4 | 57.3% | 49.3 | 587 | — |
| `mixed-scene/b-ambient.wav` | 9.94 | 44100 | 1 | 0.950 | -12.9 | 1.0% | 5.2 | 212 | no_highs |
| `mixed-scene/scene-drop.wav` | 14.00 | 44100 | 2 | 0.950 | -17.8 | 21.8% | 24.1 | 566 | — |
| `mixed-scene/v-anxious.wav` | 2.45 | 24000 | 1 | 0.950 | -15.3 | 41.7% | 20.2 | 496 | — |
| `mixed-scene/v-calm.wav` | 3.37 | 24000 | 1 | 0.950 | -16.4 | 41.7% | 16.9 | 562 | — |
| `mixed-scene/v-tired.wav` | 3.85 | 24000 | 1 | 0.950 | -17.1 | 45.7% | 26.9 | 646 | — |
| `niji-scenes/niji_ch03.wav` | 5.90 | 24000 | 1 | 0.950 | -14.6 | 39.0% | 18.0 | 595 | — |
| `niji-scenes/niji_ch04.wav` | 7.20 | 24000 | 1 | 0.950 | -15.8 | 42.6% | 19.3 | 572 | — |
| `niji-scenes/niji_ch05.wav` | 2.67 | 24000 | 1 | 0.950 | -12.7 | 29.4% | 9.7 | 573 | — |
| `niji-scenes/niji_ch08.wav` | 3.72 | 24000 | 1 | 0.950 | -15.4 | 39.8% | 22.0 | 1010 | — |
| `niji-scenes/niji_ch12.wav` | 3.87 | 24000 | 1 | 0.950 | -17.0 | 50.8% | 36.5 | 856 | — |
| `output/mashiro_morning.wav` | 3.45 | 24000 | 1 | 0.950 | -15.2 | 39.6% | 11.4 | 539 | — |
| `output_m3/mashiro_scene_morning.wav` | 3.45 | 24000 | 1 | 0.950 | -15.2 | 39.6% | 11.4 | 539 | — |
| `output_m3/mashiro_scene_night.wav` | 3.05 | 24000 | 1 | 0.950 | -15.7 | 44.3% | 21.6 | 479 | — |
| `output_regen/mashiro_morning.wav` | 3.45 | 24000 | 1 | 0.950 | -15.2 | 39.6% | 11.4 | 539 | — |
| `sound-samples/ambience-station-night.wav` | 6.00 | 44100 | 2 | 0.950 | -8.0 | 0.6% | 0.6 | 358 | — |
| `sound-samples/bgm-lonely-room.wav` | 9.94 | 44100 | 1 | 0.950 | -18.5 | 4.6% | 20.8 | 1084 | — |
| `sound-samples/bgm-train-window.wav` | 9.94 | 44100 | 1 | 0.950 | -15.5 | 2.6% | 13.3 | 186 | — |
| `sound-samples/foley-cloth-rustle.wav` | 2.00 | 44100 | 1 | 0.950 | -7.6 | 0.8% | 0.5 | 401 | — |
| `sound-samples/sfx-door-close.wav` | 2.00 | 44100 | 1 | 0.950 | -7.6 | 0.8% | 0.7 | 530 | — |
| `sound-samples/sfx-door-slam.wav` | 2.00 | 44100 | 2 | 0.950 | -19.7 | 60.4% | 45.7 | 681 | — |
| `sound-samples/sfx-glass-break.wav` | 2.00 | 44100 | 2 | 0.950 | -28.0 | 71.4% | 61.7 | 4736 | — |
| `sound-samples/sfx-gravel-steps.wav` | 4.00 | 44100 | 2 | 0.950 | -31.4 | 19.9% | 19.6 | 1215 | — |
| `sound-samples/sfx-paper-tear.wav` | 2.00 | 44100 | 2 | 0.950 | -22.5 | 76.8% | 56.6 | 5774 | — |
| `sound-samples/sfx-switch-click.wav` | 1.00 | 44100 | 2 | 0.950 | -37.4 | 97.3% | 64.8 | 4712 | — |
| `sound-samples/sfx-thunder-far.wav` | 6.00 | 44100 | 2 | 0.950 | -23.5 | 36.5% | 35.7 | 107 | bass_heavy,no_highs |

合計 37 本。注意の付いた本：3 本（`bass_heavy` / `no_highs` は生成物の性質。欠陥ではない）。
