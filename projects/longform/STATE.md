# 長尺ラン — STATE（再開のための唯一の現在地）

最終更新：2026-10-31 08:50 / 段：**P0 完了 → P1**
ユーザーは約 10 時間不在。質問しない。門を 20 分超えたら「未達」で次へ。

## この Mac（時間の数字はマシンが違えば比べられない）

| 項目 | 値 |
| --- | --- |
| 機種 | MacBook Pro 14 インチ（`Mac14,10`） |
| チップ | Apple M2 Pro / 12 コア（高性能 8 ＋ 高効率 4） |
| メモリ | 16 GB |
| OS | macOS 27.0.1 |
| 実行環境 | `/Users/user/sonic-loom-spike/venv_tsukasa`（Python 3.12） |
| 実行の型 | `PYTHONPATH=. /Users/user/sonic-loom-spike/venv_tsukasa/bin/python …` |

## 生成モデル

| 用途 | モデル | 重み | ライセンス |
| --- | --- | --- | --- |
| 声 | Tsukasa_Speech（KotoDama プロンプト） | 約 5 GB | 研究用 |
| bgm | `facebook/musicgen-small` | 約 2 GB | CC-BY-NC 4.0 |
| sfx / ambience / foley | `stabilityai/stable-audio-open-1.0` | 約 5 GB | Stability AI Community |
| 配線確認 | `stub` | なし | — |
| Resolve | ゲートウェイ経由（`SAL_RESOLVE_MODEL`） | — | — |

## 生成物の置き場（リポジトリ内・階層で分ける）

```
projects/longform/
  STATE.md            このファイル
  baseline.md         P0 の基準線（examples/ 37 本）
  timings.tsv         生成ごとの実時間（1 生成 1 行）
  acting/             P1・P2 の演技素材
    voice/            <感情>-<強度>-s<seed>.wav
    matrix.tsv        演技行列の測定
  explainer/          P3 解説
    script.yaml
    voice/  sfx/  bgm/
    renders/          統合 WAV
  drama/              P4 演劇
    script.yaml
    voice/<人物>/  sfx/  bgm/
    renders/
```

素材（1 本ずつ）と統合（renders）は混ぜない。採用分だけ最後に `examples/` へ。

## 段と状態

| 段 | 門 | 状態 |
| --- | --- | --- |
| P0 現状確認 | pytest 緑・git 実測・基準線 | **完了**（114 passed / 1 skipped、未 push 0、37 本測定） |
| P1 演技の計器 | 感情ごとに何が動いたかを数で言える | **進行中** |
| P2 演技の端 | 枠外 10 種のうち狙いの方向へ動いた数 | 未着手 |
| P3 解説 5–10 分 | 5 分以上・無音/クリップ/ヒス無し | 未着手 |
| P4 演劇 5–10 分 | 5 分以上・人物の声が分離・ducking | 未着手 |
| P5 2 パス目 | 1 パスの欠陥が全部直っている | 未着手 |
| P6 記録と納品 | 実測つき報告・examples へ・push | 未着手 |

## todo（先頭から再開する）

1. `bin/act_probe.py` を作る（f0_median / f0_range / f0_end / rate / pause_ratio / energy_median / energy_range / attack）
2. 演技行列 11 感情 × 強度 moderate × seed 1 を生成し、`acting/matrix.tsv` に測る
3. 差が出ない軸は「乗らない」と記録（無理に作らない）
4. P2：枠外 10 種（照れ/皮肉/諦め/虚勢/囁き/怒鳴り/泣き笑い/独白/早口の重なり/間）
5. P3 解説、P4 演劇、P5、P6

## P0 の実測

- `pytest tests/`：**114 passed, 1 skipped**（2.7 秒）
- `git status`：clean / `origin/main..HEAD`：**0 本**（未 push なし）
- `examples/` の WAV **37 本**を probe。注意（flags）は 3 本だけ
  （`mashiro_ch03` bass_heavy / `b-ambient` no_highs / `sfx-thunder-far` bass_heavy+no_highs）。
  一覧は `baseline.md`。
- 再生成照合：sound-samples の 11 本は既に sha1 一致を確認済み（`94c9868`）。

## 決めたこと（既定）

- 生成物はリポジトリ内の上記階層へ。`/tmp` に置いて終わらせない。
- 長い生成はバックグラウンドで流し、待つ間に別の段を進める。
- 心拍はチェックポイントごとに `資料/長尺ラン/heartbeat` を touch。20 分空けると watchdog が別セッションを起こす。
- 失敗は 1 回だけ再試行。2 回目も落ちたら failed と記録して次へ。
- 直すのは機構（engine / providers / prompts / CLI）。WAV を手で直さない。
- 測定値には定義を添える。片側だけの実測を書かない。

## 経過

- 08:43 launchd の watchdog が headless セッションを起こしたが、子プロセスが即死（launchd がジョブ終了時にプロセス群を片付ける）。
- 08:47 watchdog を「claude を前景で抱える」形に修正。`/bin/echo` で起動試験を通した。
- 08:50 P0 完了。
