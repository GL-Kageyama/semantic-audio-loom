# 参照音声（声の実体）と拡充

## 役割

参照音声は経路A（`compute_style_through_clip`）で声の **timbre を複製する元**。`.voice.yaml` の `reference_audio` に話者キー（例: `female_young_p308`）か実ファイルパスを指定すると、その声から timbre を固定して台詞を生成できる。

- 経路A（参照音声あり）：timbre は参照音声、prosody はプロンプト。
- 経路B（参照なし）：timbre も prosody もプロンプト（女性バイアスあり）。

## ライブラリ（`references/`）

老若男女 10 名。各 WAV は ~7〜9 秒クリップ（24kHz mono PCM16）。出典・ライセンスは `manifest.json` に記録。

| 出典 | ライセンス | 話者 |
| --- | --- | --- |
| CSTR VCTK Corpus 0.92 | CC BY 4.0 — Veaux, Yamagishi, MacDonald (2017) | 若〜壮年 8 名（英語） |
| Common Voice | CC0（話者は匿名 client_id） | 老人 2 名（フランス語） |

> 再配布する場合、VCTK 分は CC BY 4.0 の帰属表示が必須。

## 声を調整するとき

- **太さ・明るさを変えるのは参照の差し替え。** 経路A では `.voice.yaml` の `voice`（age / pitch / texture / breathiness / resonance）はプロンプトに入らない（`_voice_description` は経路B 専用）。効くのは `reference_audio` と、作品側の加工。
- **Direction の `pitch` 語は f0 をほとんど動かさない。** 同じ一文・同じ seed で、`female_young_p308` は `pitch: high` の有無でどちらも 282Hz、`female_adult_p225` は 244→248Hz。声を上げたいときは参照を高めの話者にするか、下の加工で半音を足す。
- **太さは f0 よりフォルマント。** 参照の F2（LPC 実測）は p225 1368Hz / p280 1981Hz / p308 2042Hz。f0 が近くても F2 が低い声は「太い」と聞こえる。
- 参照の混合比は `SAL_ALPHA`（既定 0.35、低いほど参照 timbre を保持）と `SAL_BETA`（既定 0.7、低いほどプロンプト由来の演技）。作品の cue で `alpha` / `beta` を上書きできる。
- 生成後の加工は作品の `voice_fx.yaml`（`assemble.py`）。`highpass_hz` / `lowpass_hz` / `gain_db` / `pitch_semitones`。`pitch_semitones` はフォルマントも一緒に上がるので、小さな機体・マスコットの声に向く。

## 拡充（足りない声への方針）

特定の声（例：男性老人）が弱い場合、**使用者が声を拡充して参照に指定する**のが既定。開発者が全声を揃えない。

- `bin/reference.py synthesize <key> --character <name>` … ローカル生成（経路B・参照不要）。キャラの voice.yaml から age/gender/pitch/texture を入力。
- `bin/reference.py add <wav> <key> --license … --source …` … 著作権フリー音源の登録。

注意：`synthesize`（経路B）は女性バイアスが強い。男性の深い声・老人は `add`（著作権フリー音源）が向く。登録時は必ず出典・ライセンスを `manifest.json` に記録する。
