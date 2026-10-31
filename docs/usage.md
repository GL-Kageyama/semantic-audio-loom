# 使い方 — 全 CLI

## 参照音声の拡充（bin/reference.py）

```bash
bin/reference.py list                                    # 登録済み参照音声一覧
bin/reference.py synthesize elderly_man --character mashiro   # ローカル生成（経路B・参照不要）
bin/reference.py add my_voice.wav old_woman --gender F --age sixties \
    --license "CC0" --source "Common Voice"               # 著作権フリー音源を登録
```

経路B（ローカル生成）は女性バイアスが強い。男性・老人の確実な声は `add`（著作権フリー
音源の登録）が向く。詳細は [reference-voices.md](reference-voices.md)。

## キャラ作り（bin/character.py）

```bash
bin/character.py init mashiro            # characters/mashiro.voice.yaml を生成
bin/character.py validate mashiro        # スキーマ検証
bin/character.py list                    # 登録済みキャラ一覧
```

## 演技の振り付け（bin/performance.py）

```bash
bin/performance.py init anxious-night-call
bin/performance.py validate anxious-night-call
bin/performance.py list
```

## 声の生成（bin/generate.py）

```bash
bin/generate.py --character mashiro --performance anxious-night-call \
    --project demo --scene night \
    --line "……まだ、起きてる？" --name mashiro_night
```

- キャラ + 演技を名前で再利用。未指定の演技フラグは資材値を引き継ぐ。
- `--emotion joy` など CLI フラグで演技資材を上書きも可。
- `--resolve llm`（既定）で Resolve を LLM に、`--resolve rule` で決定的写像（API なし）。
- `--situation` と `--state-file`（character_state の YAML）が subtext 推論の入力。
  `--subtext` で人間が裏の意味を直接指定もできる。
- 台詞は日本語（Tsukasa は `phonemize` で読みへ変換）。`--seed` で再現可能。
- 漢字の読みが誤読される語（例: `既読`→`きよみ`）は、`--line` 内でふりがなを指定できる。
  `漢字《かな》` の記法で、`《》` は読みにだけ使われ、保存される台詞からは外れる。

  ```bash
  --line "既読《きどく》を付けて、画面を閉じる。"   # 「きどく」と発音
  ```

- キャラ名（固有名詞）は `characters/*.voice.yaml` の `name_reading` に読みを書いておくと、
  台詞中のその名前へ自動でふりがなが振られる（`《》` を手で書かなくてよい）。語り（ナレーション）
  などで話者が本人でない場合に有効。例: 真白（`name_reading: ましろ`）→「真白は」が「ましろは」
  と発音される。手書き `《》` と自動ふりがなは共存でき、両方とも読みへ反映される。

## 音の生成（bin/asset.py）

bgm / ambience / sfx / foley を声と同じ 7 段フローで作る。

```bash
bin/asset.py --type bgm --project demo --name lonely-room \
    --sound role=underscore --sound mood=lonely --sound instrumentation=solo_piano \
    --duration 20                                  # 既定 Resolve=llm

bin/asset.py --type sfx --project demo --name door-close \
    --sound event="heavy wooden door closing" --duration 3 \
    --resolve rule --provider stub                  # 依存なしで配線を確認

bin/asset.py --type ambience --sound-file rain.yaml --duration 30 \
    --save-library steady-rain --tags rain,night    # ライブラリへも取り込む
```

- Direction は `--sound key=value`（複数可）。カンマ区切りは配列、`{...}` は JSON。
- `--duration` / `--prompt` / `--situation` / `--subtext` / `--seed` / `--provider`。
- `--bible` を省略すると `projects/<project>/sound-bible.yaml` を自動で読む（`--no-bible` で無効）。
- プロンプトは英語（モデル向け）。詳細は [asset-generation.md](asset-generation.md)。

## ライブラリ（bin/library.py）

```bash
bin/library.py list [--type sfx]
bin/library.py search "rain night" [--type ambience]
bin/library.py show door-close
bin/library.py add my_rain.wav --type ambience --name steady-rain --tags rain
bin/library.py validate
```

詳細は [library.md](library.md)。

## Sound Bible（bin/sound-bible.py）

```bash
bin/sound-bible.py init demo       # projects/demo/sound-bible.yaml
bin/sound-bible.py show demo
bin/sound-bible.py validate demo
```

詳細は [sound-bible.md](sound-bible.md)。

## 生成物を測る（bin/probe.py）

聴く代わりに、形式・レベル・帯域・無音率・先頭の段差を数で出す。良し悪しは判定せず、
機械的に明らかな欠陥（無音・クリップ・2kHz 以上の完全な欠落・先頭の段差）だけを注意する。

```bash
bin/probe.py projects/demo/assets/sound/bgm.wav
bin/probe.py examples/sound-samples/*.wav --json
```

帯域と重心は**ファイル全体**を覆う窓（8192 サンプル・半分ずつ重ねる）の平均で測る。
先頭だけを測ると、曲ではなく鳴り始めの一瞬を測ることになり、同じプロンプトでも
seed ごとに `bass_heavy` と `no_highs` が入れ替わる。窓より短い音は窓を縮めて測り、
256 サンプル未満（32kHz で 8 ミリ秒）では帯域を出さず `too_short` を注意する
（0 dB と書くと「全体と同じ」に見えるため）。

判定線は実在曲で裏を取ってある。`音源調査/_openlofi` の 166 曲を同じ窓で測ると、
低−中の差は中央 4.3 dB・最大 11.4 dB、高域は最小 −41.2 dB。注意の線は
低−中 12 dB・高域 −45 dB で、実曲の外側にある。ただし較正は lofi 1 ジャンルなので、
意図して低域を張る曲（サブベースもの）は `bass_heavy` で正しく外れる——注意は
「欠陥」ではなく「実曲の範囲から外れた」の意味で読む。

**量は全チャンネルで測る。** `peak`・`rms_db`・`crest_db`・`clipped` は波形の
全サンプルが対象。モノラルへ落としてから測ると、左右の相関が低い音ほど小さく出る
（相関 0.25 の sfx で peak 0.95 → 0.69・RMS −2 dB）。帯域・重心・無音率・起伏は
モノラルで測る（どれも「何が鳴っているか」の話で、量ではない）。

**起伏（`burst_db`）**は 10ms 包絡の最大−中央値。帯域と重心は「何が鳴っているか」しか
言わないので、sfx が**点で鳴ったか**はここで見る。クリック・打撃は 15 dB 以上、連続音
（ヒス・パッド・環境音）は数 dB になる。`sfx` に頼んだ音が 3 dB なら、それは
「クリックの音色の持続音」であってクリックではない。

## 演技を測る（bin/act_probe.py）

`probe` は音の物理しか見ない。演技——声の高さ・抑揚の幅・語尾の上げ下げ・速さ・間・
張り・出だしの勢い——はこちらで測る。良し悪しは判定せず、**感情ごとに何が動いたか**を
数で言えるようにするためだけの計器。

```bash
bin/act_probe.py projects/longform/assets/acting/*.wav
bin/act_probe.py --tsv projects/longform/assets/acting/*.wav > matrix.tsv
```

| 指標 | 定義 |
| --- | --- |
| `f0_median_hz` | 有声フレームの基本周波数の中央値（pyin） |
| `f0_range_st` | 有声 f0 の 5〜95 パーセンタイルの幅（半音） |
| `f0_end_st_s` | **100ms 以上続いた最後の有声区間**の末尾 200ms の f0 の傾き（半音/秒） |
| `rate_mora_s` | 鳴っている時間（−50 dBFS 以上）あたりの包絡の山（モーラ概算） |
| `pause_ratio` | 発話の端から端までのうち −50 dBFS 未満の割合。冒頭・末尾の無音は数えない |
| `energy_median_db` / `energy_range_db` | **有声フレームだけ**の 10ms 包絡 dB の中央値と p95−p5 |
| `attack_ms` | 最初に −40 dBFS を超えてから 300ms 内の包絡の最大までの時間 |
| `voiced_fraction` | 有声と判定されたフレームの割合 |

`f0_end` をファイル末尾でなく「最後に続いた声」から測るのは、TTS の後ろの無音を
測るとどの感情でも「測れない」になるため。さらに、間をまたいで直線を引くと
間の前後の別の音節を 1 本の傾きに混ぜ、350→220 Hz の飛びが −54 半音/秒になる。
f0 の追跡は 2 段（全体で当たりを付け、中央値の上下 1 オクターブに絞って取り直す）。
有声は pyin の有声確率 0.3 以上だけを数える（減衰・残響の尾は 0.02 程度）。
速さの分母は「鳴っている時間」で、間は `pause_ratio` が別に測る。
`energy` を有声区間に限るのは、無音を混ぜると範囲が 100 dB を超え、感情の差でなく
「間の長さ」を測ってしまうため。測れない値は 0 でなく `None`（0 は「無い」ではなく
「全体と同じ」に見える）。

## シーン合成（bin/scene.py）

複数人物の台詞を「間（無音）」で連結し、1 つの WAV にする。`scene.yaml` がキュー
（キャラ＋台詞＋Direction＋`pause_before`）を宣言し、各キューを voice 生成で作ってから連結する。

```bash
# 生成（scene.yaml → scene.wav + scene.params.yaml）
bin/scene.py --scene-file examples/gozen-niji-ch01/scene.yaml --project gozen-niji

# 再生成（保存済み Spec を再利用・LLM なし＝seed決定論）
bin/scene.py --params examples/gozen-niji-ch01/gozen-niji-ch01.params.yaml --out-dir /tmp/regen
```

- `--scene-file`（render）と `--params`（regen）は排他。片方必須。
- 間（余白）＝無音。`default_pause`（秒）が各キューの既定、`pause_before`（秒）で個別上書き。
- 環境音・BGM・ducking・パンは将来スコープ。詳細は [scene.md](scene.md)。

## 統合（bin/mix.py）

生成済みの音を、時刻と利得と役割だけで 1 本に重ねる。生成はしない。
役割は **bed**（bgm・ambience＝下に流す）、**voice**（台詞）、**hit**（sfx・foley＝点で鳴る）。
bed は voice が鳴っている間だけ沈む（ducking）。天井は最後に一度だけ掛ける。

```yaml
sample_rate: 44100
output: scene-mix
stems:
  - {file: bgm.wav,       role: bed,   start: 0.0, gain_db: -20}
  - {file: line-01.wav,   role: voice, start: 0.5, gain_db: 0}
  - {file: door-slam.wav, role: hit,   start: 1.2, gain_db: -6}
duck: {threshold_db: -30, depth_db: 10, attack_s: 0.02, release_s: 0.35}
master_peak: 0.95
```

```bash
bin/mix.py --file mix.yaml --out-dir projects/demo/assets/combined --json
```

- チャンネル数はステムの最大（`channels` で明示も可）。mono の声は両耳の真ん中へ
  複製、ステレオの sfx は左右を保つ。ステムを mono へ落としてから混ぜると、左右の
  相関が低い音ほど小さくなる（相関 0.25 で −2 dB）。パンを動かす指定はまだ無い。
- `duck` は声の 5ms 包絡が閾値を超えた分だけ bed を下げ、`depth_db` で頭打ち。
  戻り（`release_s`）を速くすると、声の合間に bed が息継ぎして聞こえる。
- `ducked` が `false` のときは bed が無いか声が無い。生成側の欠落として読む。

## 再生成（bin/regenerate.py）

保存済み Spec を再利用・LLM は呼ばない（再現性）。

```bash
bin/regenerate.py examples/mashiro-night/mashiro_night.params.yaml \
    --out-dir /tmp/regen
```

## 蒸留（bin/distill.py）

手で埋める `init` の代わりに、物語・脚本・人物描写からキャラと演技を自動生成する：

```bash
bin/distill.py batch story.txt                    # 一括蒸留：物語 → 主要キャラ複数 × 代表シーン複数
bin/distill.py character "金髪で低い声の青年" --name rei      # 単発：キャラ1体
bin/distill.py performance "深夜、返事が怖い電話" --name anxious-call  # 単発：演技1つ
```

`--synthesize` でキャラの元音声（経路B）も生成・登録、`--dry-run` で書き出さず YAML を確認。
設計（理解→選択→翻訳・schema 制約）は [distill.md](distill.md)。
