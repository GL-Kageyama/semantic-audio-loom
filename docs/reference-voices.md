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

## 拡充（足りない声への方針）

特定の声（例：男性老人）が弱い場合、**使用者が声を拡充して参照に指定する**のが既定。開発者が全声を揃えない。

- `bin/reference.py synthesize <key> --character <name>` … ローカル生成（経路B・参照不要）。キャラの voice.yaml から age/gender/pitch/texture を入力。
- `bin/reference.py add <wav> <key> --license … --source …` … 著作権フリー音源の登録。

注意：`synthesize`（経路B）は女性バイアスが強い。男性の深い声・老人は `add`（著作権フリー音源）が向く。登録時は必ず出典・ライセンスを `manifest.json` に記録する。
