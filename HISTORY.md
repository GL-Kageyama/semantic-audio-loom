# HISTORY — 開発履歴

日付入りの変更経緯・過去の設計との比較・実測値はここに記録する。現在の情報は README / docs / SKILL を見る。

## 2026-10-31 — 長尺ラン（演技の計器・5 分の作品 2 本）

### スコープ

5〜10 分の音を 2 本（解説と二人芝居）作りながら、「演技がどこまで届くか」を測った。
実測と経過は [projects/longform/REPORT.md](projects/longform/REPORT.md) と
[projects/longform/STATE.md](projects/longform/STATE.md)、納品は
[examples/longform-explainer/](examples/longform-explainer/) と
[examples/longform-drama/](examples/longform-drama/)。

### 足した道具

- `bin/act_probe.py` ＋ `semantic_audio_loom/skills/act_probe.py` … 演技を数にする計器
  （f0 中央値・抑揚・語尾の傾き・速さ・間の比・張り・立ち上がり）。
- `projects/longform/assemble.py` … キューを切って並べ、声量を `gain_db` で戻し、
  効果音を cue 名の錨で置き、下地を継ぎ足し、ducking つきで 1 本にする。
- `projects/longform/check_render.py` … 尺・ピーク・クリップ・無音・効果音の立ち上がり。
- `projects/longform/check_duck.py` … 下地が実際に何 dB 沈んだかを測る。
- `characters/narrator.voice.yaml` … 語り手（参照音声 `female_mature_p294`）。

### 直した機構の穴

1. `intensity` が `_spec_prompt` に渡っていなかった（anger の subtle と strong が
   **バイト一致**）。`_INTENSITY_PHRASES` を追加。
2. `pitch` を `capabilities()` が名乗るのに散文へ渡していなかった。`PITCH_PHRASES` を追加。
3. `volume`（whisper〜shout）が `effort` に潰れて囁きが消えていた。`loudness.volume` を
   schema・resolve・provider に通した。

### 実測（M2 Pro / 16 GB・`venv_tsukasa`）

- 11 感情（moderate・seed 1）：f0 329.7〜359.6 Hz（1.5 半音）・抑揚 8.3〜9.2 半音。
  **seed の揺れ（joy s1→s2 で 2.9 半音）のほうが感情差より大きい。**
- 枠外 10 種を seed 1〜5 で振り直した（55 本）。**確実に動くのは時間だけ**
  （早口 5/5・間 5/5、遅いと指定した 5 種も長さは 5/5）。張り・高低・抑揚・語尾・息は
  1〜3/5 で、seed の揺れと区別できない。seed 1 本だけで「完全 4」と読んだのは誤りで、
  基準線そのものの f0 が 5 本で 241〜326 Hz（5.2 半音）揺れる。
  速さに随伴する立ち上がりだけは 5/5 で分かれた（諦め 190・早口 80・間 270 ms／基準 140 ms）。
- 声量の指示は生成音のレベルに出ない（normal −17.7 / quiet −17.8 dB。全部 peak 0.95）。
  pitch の指示も f0 を動かさない（0.3 半音）。差はミックスの `gain_db` で作る。
- 同じモデルの二人は声で分かれない（同じ台詞の MFCC 距離：同一人物 11.7〜13.2／別人 7.2）。
  帯域（320–3400 Hz）で分けた。組み上げ後は低域 −5.3 dB・高域 −9.3 dB。
- 生成時間（1 本）：stable_audio 1.6〜4 秒の素材で 392〜755 秒、musicgen 30 秒で 182 秒、
  Tsukasa の声は 1 本 1.0〜4.2 秒（モデルのロードは 1 プロセス 1 回）。
- 完成：解説 311.2 秒（クリップ 0・効果音 10 本すべて +15 dB 以上・ducking −11.7 dB）、
  演劇 310.5 秒（呼び出し +40.1 dB・切断 +22.1 dB・ducking −11.2 dB）。

### 感情は言葉の側でなくノブの側だった

- 11 感情の側も seed 5 で振り直した（10 感情 × 5 seed＋基準線＋強度＝85 本）。
  **8 指標のどれでも基準線から 5/5 で分かれない。** 散文は感情ごとに違う
  （`params.yaml` の emotion が別）のに、音は seed の揺れの中に留まる。
- 疑う先を言葉から `beta`（プロンプト由来の演技成分を混ぜるノブ・既定 0.7）へ移し、
  同じ台詞・同じ seed で 0.7 / 0.5 / 0.3 を振った（4 感情 × 5 seed × 3 段＝60 本）。
  f0 中央値は neutral 290 → 271 → 257 Hz、anger 311 → 322 → 320、joy 315 → 324 → 326、
  sadness 292 → 292 → 284。**seed の揺れが 29 → 12 Hz に縮み、感情の差が残る。**
  0.3 で高覚醒（anger・joy）と低覚醒（neutral・sadness）は重ならない。anger と joy は重なる。
- 強度（subtle 0.25 / strong 0.75）も beta 0.3 で分かれる（30 本）。strong は f0 が
  anger +31.2・joy +20.2・sadness +45.2 Hz（同じ seed で 5/5）。0.7 では分かれなかった。
- 代償は声質。`references/mashiro.wav` との MFCC 距離は 0.7 で 17〜19、0.3 で 40〜53
  （種の中の広がり 20.6）。**演技は声そのものを動かして出ている。**
- 意味の写像ではない：sadness の strong で f0 が**上がる**。beta を下げると neutral 自身も
  動く（290 → 257 Hz）。感情の一文は「演技だけを足す」のではなく、声全体の寄せ先を変える。
- `SAL_ALPHA` / `SAL_BETA` を `config.py` に足した（測定用。params.yaml には実値が残るので
  再生成の照合は崩れない）。beta は 1 本ごとには振れない（プロセス全体）。
- 台詞を変えても残る（beta 0.3・3 台詞 × 4 感情 × seed 3＝36 本）：anger と joy は
  どの台詞でも 3/3 で neutral より上、sadness は 8/9。**文の長さ・内容に依らない**
  （台詞の長さの中央値 2.67 / 2.47 / 2.99 秒）。
- 参照音声を変えても同じ（beta 0.3・mashiro / narrator / niji × 4 感情 × seed 3＝24 本）：
  3 つとも neutral < sadness < anger ≈ joy。上がり幅は anger で +63 / +70 / +68 Hz。
  **分かれ方は声の個性でなく混ぜ方の側の性質。**
- 道具：`projects/longform/acting-matrix/summarize_matrix.py`（5/5 判定と
  基準線の幅との比較）、`projects/longform/summarize_beta.py`、`projects/longform/measure_timbre.py`。

### 語尾の抑揚も計器に載せた

- `prosody.intonation` は rule Resolve が `neutral` 固定で、Direction からも CLI からも
  届かなかった。Direction の欄・`--intonation`・schema 3 本・`PERF_ENUMS` に通した。
- rising / flat / falling × seed 5 を beta 0.7 と 0.3 で振った（60 本）。
  rising が falling より上に出た seed は **3/5 と 2/5**。beta 0.3 の中央値は狙いどおり
  （+2.16 / +1.26 / −0.17 半音/秒）だが、種の振れ幅 −19.3〜+16.8 が差を飲む。
- `build_voice.py` は `script.yaml` の `beta:` / `alpha:` を cue ごとに読む
  （プロセスの既定は持ち越さない。実値は params.yaml と timings に残る）。
- 聞き比べの見本を `examples/longform-acting/` に足した（74 秒・同じ台詞を
  beta 0.7 と 0.3 で並べる）。

### beta 0.3 の端を測った（alpha・pitch・感情の外の軸・決定論・感情×delivery）

- **alpha**（`ref = alpha × 予測 + (1 − alpha) × 参照` の係数・48 本）を 0.20〜0.70 に
  振っても、感情の分かれ方は 3/3 のまま、参照音声との MFCC 距離は 54〜57 で動かない。
  **alpha は演技を失わずに振れる。**
- **pitch**（36 本）は beta 0.3 で効く：neutral 257 → 266 → 277 Hz。参照は 297 Hz。
  ただし MFCC 距離は戻らず、`high` で 67.2（natural 56.2）。**音程は戻り、声質は戻らない。**
  beta 0.7 では pitch の指示が f0 を動かさなかった（ノブの効く側が beta で決まる）。
- **感情の外の軸**（30 本・neutral）：速さは 3.72 / 2.40 / 1.97 秒、delivery は
  desperate 302・aggressive 284・intimate 276 Hz と 3/3 で動き、cold は動かない。
  声量は量を動かさない（ピークは全部 0.95。三層分業の設計どおり）。
- **breathiness は配線されていなかった**：Direction・schema・CLI が受けるのに Spec にも
  散文にも載らず、heavy と none がバイト一致した。`prosody.breathiness` を schema・
  rule 解決・provider（`BREATHINESS_PHRASES`）へ通した。配線後は平坦度が
  0.0169 → 0.0191（+13%）へ動くが、seed 3 で 1 本逆転する（2/3）。
- **決定論は最後のビットまでではない**：同じ設定で別プロセスから作り直した 12 本のうち
  5 本がバイト不一致。差は RMS 0.0005〜0.0007（信号比 −65 dB 前後）で長さは同じ。
  「同じ seed で byte-identical」ではなく「同じ長さで、差は −65 dB 程度」と書く。
- **感情 × delivery**（27 本・neutral / anger / joy × cold / cheerful / aggressive）：
  f0 は neutral の cold / cheerful / aggressive が 257 / 294 / 284、anger が
  294 / 345 / 353、joy が 309 / 341 / 351 Hz。**どちらの振り幅も 40〜60 Hz** で、
  型のほうが感情を消さない（anger + cold は 294 で、neutral 単独の 257 より上）。
  ただし足し算ではない（anger の上がり幅は cold +37・aggressive +69 で一定しない）。
- **beta の床**（`acting-beta-low/`・36 本・alpha 0.35）：0.2 / 0.1 / 0.0 まで下げた。
  anger − neutral は 0.3 で +63.2（MFCC 距離 45.8）、0.2 で +65.7（51.2）、0.1 で
  +85.0（62.3）、0.0 で +87.8（68.9）。seed の揺れは 8.8 → 8.5 → 5.7 → 3.0 Hz で、
  0.0 の anger は seed 1〜3 が 327.8 / 327.9 / 327.8 Hz。**演技は伸び続けるが、
  0.3 より下は距離のほうが速く増える。** 抑揚（7.8〜8.4 st）・速さ・間・張り幅は
  どの段でも崩れない（耳で確かめてはいない）。
- **抑揚の言葉を床（beta 0.0）で振った**（`acting-inton-000/`・15 本）：rising / flat /
  falling の順序は seed 5/5 で揃う（0.3 では 2/5）。ただし語尾はどの条件でも
  +13.8〜+14.7 半音/秒で上向き、語による差は 0.95 半音/秒（seed 3 は 14.32 対 14.29）。
  語は中央の音高も動かす（rising 238.6 対 flat 248.5 Hz）。傾きの向きはプロンプトの
  文面が決め、`intonation` はその上に小さく乗る。
- **演劇を beta 0.3 で組み直した**（`drama-beta03/`・89 本・332.2 秒）。生の声は元と
  同じ長さ（271.1 対 271.3 秒）なのに、頭尾を切った後の声は 21.7 秒長い（239.0 対
  217.3 秒）。**beta 0.3 の声は無音の割合が低く、語りが長く続く。** MFCC 距離は
  34.3 → 46.5。門は通った（ピーク −0.4 dBFS・クリップ 0・呼び出し +40.0 dB・
  切断 +20.0 dB・ducking −11.3 dB）。納品は `examples/longform-drama-beta03/`。

## 2026-10-31 — M5 音の生成＋ライブラリ（5 種すべて）

### スコープ

- 正典 5 種のうち voice しか動いていなかった状態から、bgm / ambience / sfx / foley を
  同じ 7 段フローに乗せた。資材の範囲は 5 種すべて、生成はローカル優先（クラウドは任意）、
  最初の縦の一本は「生成＋ライブラリ」（ユーザー選択）。
- Scene（複数 voice の連結）は正典 5 種に数えないまま。Timeline / Mixer（重ね合わせ・
  ducking・LUFS）は M6、脚本→音の設計図は M7。

### 設計

- Seam（モデル非依存の境界）を type 別の Spec に一般化：voice=Performance Spec、
  bgm=Music Spec、ambience・sfx・foley=Sound Spec。`GenerationRequest` は
  `performance_spec` をやめて `spec` ＋ `asset_type` を持つ（`performance_spec` は
  後方互換の property として残す）。
- `GenerationIntent.sound`（dict）を追加。voice の Direction フィールドはそのまま。
- Resolve は type で分岐。Rule は構造フィールドを Spec へ移し、英語プロンプトを組み立てる。
  LLM は 3 つのプロンプト（resolve / resolve_music / resolve_sound）を使い分ける。
- Route は asset_type ごとの既定 Provider を持ち、`capabilities()["asset_types"]` で
  非対応を即座に落とす（生成してから気づかない）。
- 保存形式は type 別（`config.OUTPUT_FORMATS`）。voice は従来どおり 24kHz mono、
  音の 4 種は 44.1kHz・チャンネルは生成のまま。Normalize にリサンプルとチャンネル変換を
  足し、ループ資材には末尾フェードを掛けない。
- 新規スキーマ：`music_spec` / `sound_spec` / `sound_bible` / `library_asset`。
- 新規 Provider：`musicgen`（transformers・musicgen-small・32kHz mono・30 秒）、
  `stable_audio`（diffusers・stable-audio-open-1.0・44.1kHz stereo・約 47 秒・gated）、
  `stub`（依存なし・決定的）。
- 新規 CLI：`bin/asset.py`（音の生成）、`bin/library.py`（一覧・検索・追加・検証）、
  `bin/sound-bible.py`（init/show/validate）。
- ライブラリは `library/<type>/<name>.asset.yaml` ＋ `.wav`。検索は埋め込みでなく
  意味フィールド・タグ・プロンプトの部分一致を数える決定的な方式。
- `projects/` の解決を `config.project_dir()` に一本化（`SAL_PROJECTS_DIR` で差し替え可）。

### 検証

- `pytest tests/` … 95 passed（既存 55 ＋ 新規 40）。重いモデルは使わず stub で全 type の
  7 段フロー・保存形式（チャンネル／サンプルレート）・ライブラリの追加と検索・Sound Bible の
  継承規則・Route の非対応拒否を通した。i18n は `resolve_music` / `resolve_sound` の
  プロンプトが `--lang` で切り替わること（かな漏れ無し）をモック LLM で確認した。
- CLI 実測（stub）：`sound-bible init → asset(bgm/ambience) → library list/search/validate
  → regenerate` が通り、regenerate は同じ seed で走った。
- **musicgen は本物の重みで通した**（`facebook/musicgen-small`・CPU・M2 Pro）。3 秒と 5 秒の
  BGM を生成 → リサンプル（32kHz → 44.1kHz）→ 保存まで通り、wav は peak 0.95・RMS 0.176
  （−15 dBFS）・無音率 0.08%・末尾フェードあり。所要は 5 秒の BGM で約 37 秒（重み取得済み）。
  初回は重み 2.2GB の取得を含めて約 2 分。
- **stable_audio は未実測**。モデルが gated で、この環境には diffusers も HF のトークンも
  無い。ライセンス同意と `huggingface-cli login` のあとで `--provider stable_audio` を
  通すのが次の実測。ambience / sfx / foley の保存形式は stub でのみ確認している。
- 空の検査を「健全」と言わないよう直した：ライブラリ 0 件の `library.py validate` と、
  全節が空の Sound Bible の `validate` は、OK でなく「空」と報せる。
- サンプルを採る途中でプロンプトの欠陥が 2 つ出た（どちらも本物のモデルで音を出すまで
  見えなかった）。**Rule 解決が日本語の `situation` をそのままモデル向けプロンプトへ
  足していた**——MusicGen / Stable Audio は英語で学習した T5 を使うので、日本語は
  無意味なトークン列になる。日本語の状況は `subtext` にだけ残し、英語のときだけ
  プロンプトへ足すようにした。また、`About 10 seconds.` の後ろに `.` を重ねて
  `..` になっていた（区切りを 1 つにした）。Direction に日本語を直接書いた場合は
  非英語がプロンプトに残る旨を警告する（黙って渡さない）。

### 出力を測る（耳の代わりのループ）

生成した音を聴く代わりに測る道具を足した（`semantic_audio_loom/skills/probe.py`・
`bin/probe.py`）。形式・レベル・帯域・無音率・重心・先頭サンプルを出し、機械的に
明らかな欠陥（無音・クリップ・2kHz 以上の完全な欠落・先頭の段差）だけを注意する。
良し悪しは判定しない（曲が暗いのは趣味のことがある）。

- **先頭の段差**：生成モデルは曲の途中から鳴り始めることがあり、`bgm-train-window` は
  先頭サンプルが −0.2416 で始まっていた（無音からの段差＝プツッ）。Normalize に
  2 ms の頭のランプを足した（声とループ資材には掛けない）。
- **尺の切り捨て**：Provider は上限で切るが（MusicGen 30 秒・stub 8 秒）、黙って
  短い資材を返していた。Route が `max_seconds` を超えたら stderr に出すようにした。
  stub も上限を名乗っていなかったので足した。
- **bgm のプロンプト形**：同じモデル・同じ seed で、属性の羅列と音の説明文を比べた
  （musicgen-small・5 秒・guidance 3.0。`mid-low` は 250–1000 Hz と 0–250 Hz の
  平均の差で、大きいほど楽器の帯域に寄る）：

  | プロンプト | s7 | s99 | s123 |
  | --- | --- | --- | --- |
  | `lonely, featuring felt piano, 60 BPM, understated background score, instrumental, no vocals. About 5 seconds.` | −14.1 | −10.2 | −2.2 |
  | 上と同じ（`About 5 seconds.` なし） | −10.1 | +0.8 | — |
  | `A felt piano piece, lonely and still, at 60 BPM, understated background score, instrumental.` | −10.8 | +15.3 | — |
  | `A piece of music, felt piano, 60 BPM, understated background score, instrumental, no vocals.` | −6.6 | −0.2 | — |
  | `A soft solo felt piano piece.` | +22.0 | +11.3 | — |
  | `A felt piano piece, warm close-miked recording, gentle sustain, sparse melody.` | −6.6 | +19.2 | — |
  | `A soft solo felt piano piece, slow and spacious, warm close-miked recording, gentle sustain, sparse melody.` | +34.7 | +29.2 | +28.4 |

  羅列は seed で振れて低域に寄る。説明文は 3 seed とも +28〜35 dB。短い説明文
  （`A soft solo felt piano piece.`）でも +22.0 / +11.3 と正に出る。属性を後ろに
  足しただけの形は振れる（−10.8〜+19.2）。Rule 解決のプロンプトを、楽器を主語に
  した一文へ組み替えた。`no vocals` は書かない（モデルは否定を演算せず、`vocals` を
  名指しするだけになる）。LLM 解決（`prompts/*.json` の `resolve_music`）の指示も
  同じ形へ揃えた（3 言語とも）。

  同じ seed 42・同じ Direction の保存サンプルで確認：旧プロンプトは低域が中域より
  3.5 dB 大きく（正規化前の生波形で測った。ピーク正規化は両帯域に同じ利得なので差は
  変わらない）、新プロンプトは低域が中域より 18.7 dB 小さい（9.94 秒）。条件あたりの seed 数は上表のとおりで、5 秒の
  生成 1 回ずつ。同じプロンプト・同じ seed で再生成すると sha1 が一致する
  （musicgen の 2 本のサンプル）ので、この差は seed の揺れではない。

### 測り器の欠陥（先頭 0.2 秒だけを測っていた）

bgm を 5 パターン × 複数 seed で回したところ、同じプロンプトで注意の出方が
seed ごとに入れ替わった。原因は生成ではなく `probe` の側だった。帯域・重心を
`mono[:8192]` の 1 回の FFT で出しており、32kHz で **0.26 秒**、44.1kHz で
0.19 秒——曲ではなく鳴り始めの一瞬を測っていた。打楽器は頭の 1 拍で低域に、
爪弾きは頭のアタックで高域に寄るので、判定が反転する。

全長を覆う窓（8192 サンプル・半分ずつ重ねる）の平均へ直した。同じ 9 本の再測：

| ファイル | 先頭 0.26 秒での帯域（低/中/高） | 全域での帯域 | 先頭の注意 → 全域 |
| --- | --- | --- | --- |
| felt-guitar（seed 45） | −0.2 / −13.5 / −47.0 | −0.3 / −11.6 / −32.4 | `bass_heavy` `no_highs` → なし |
| felt-guitar-47 | −0.2 / −13.1 / −27.4 | −1.9 / −4.6 / −32.8 | `bass_heavy` → なし |
| techno-loop（seed 44） | −0.6 / −23.5 / −9.2 | −0.3 / −18.9 / −13.5 | `bass_heavy` → `bass_heavy`（3 seed とも再現） |
| rock-drive | −3.3 / −4.2 / −8.1 | −2.1 / −5.9 / −9.3 | なし → なし |
| waltz-window | −33.2 / −0.1 / −18.8 | −32.1 / −0.3 / −11.4 | なし → なし |

判定線は実在曲で裏を取った。`音源調査/_openlofi` の 166 曲（mp3 → 44.1kHz mono）を
同じ窓で測ると、低−中の差は中央 4.3 dB・最大 11.4 dB、高域は最小 −41.2 dB。
注意の線（低−中 12 dB・高域 −45 dB）は実曲の分布の外側にある。較正は lofi 1
ジャンルなので、意図してサブベースを張る曲は `bass_heavy` で正しく外れる
（techno-loop は「sub bass の曲」と書いて頼んでいるので、外れるのが正しい）。
注意は「欠陥」ではなく「実在曲の範囲から外れた」の意味で読む。

短い音では帯域を 0.0 dB と書いていた（「無い」が「全体と同じ」に見える）。
256 サンプル未満は帯域を `null` にし、`too_short` を注意する。作り物の音で
6 本の検査を足した（先頭 0.3 秒だけ低音で残りが 440 Hz の音を「高音の曲」と
答えること、等）。`pytest tests/` は 100 passed / 1 skipped。

### 測り器の欠陥 2（点で鳴ったかを測っていなかった）

帯域と重心は「何が鳴っているか」しか言わない。sfx にクリックを頼んでも、
ヒスが返れば「高域が多い」と正しく答えてしまう。sfx の依頼（点で鳴る）が
満たされたかは、別の計器が要る。

`burst_db`（10ms 包絡の最大 − 中央値）を足した。クリック・打撃は 15 dB 以上、
持続音（ヒス・パッド・環境音）は数 dB。注意（flag）ではなく数として出す——
同じ数字が bgm では正常、sfx では欠陥なので、型を知らない `probe` が
判定を持ってはいけない。

### stable_audio が一度も実モデルで走っていなかった

sfx の実生成が `RecursionError` で落ちた。`CosineDPMSolverMultistepScheduler`
は ODE の枝を持たず、SDE の区間増分を torchsde の BrownianTree から取る。
diffusers 0.31 + torchsde 0.2.6 + Python 3.12 では木の構築
（`_Interval.__init__` → `_split`）が再帰の上限に当たる。再帰上限 200,000 と
256 MB のスレッドスタックでは直らなかった。

木が要るのは区間を跨いで問い直すときで、前へ進む掃引では重ならない区間の増分が
独立な正規で足りる。スケジューラは `noise_sampler is None` の枝で建てるので、
名前を `_GaussianNoiseSampler` へ差し替えて torchsde を経路から外した。

**最初の差し替えは間違っていた。** 増分を `sqrt(t1² − t0²)` で掛けて返したが、
`BrownianTreeNoiseSampler` は木の増分を `sqrt(t1 − t0)` で割って**単位分散**を
返し、縮尺 `sigma_t * sqrt(1 − exp(−2h))` はスケジューラが掛ける。σ が 500 の帯で
86 倍のノイズが乗り、出力はプロンプトでなくヒスになった。

| 同じ 6 本（プロンプト × 尺、20 ステップ） | 起伏 `burst_db` | 無音率 | 読み |
| --- | --- | --- | --- |
| 誤った縮尺 | 0.4 〜 4.7 dB | 0.01 〜 0.61 | 連続のヒス。クリックではない |
| 単位分散 | 51 〜 99 dB | 0.96 〜 0.99 | 一発の音＋ほぼ無音 |

**テストが誤りを固定していた。** 増分の分散を検査するテストを自分で書き、
自分が信じた契約（区間の幅を掛ける）をそのまま書いたので緑のまま通った。
契約（単位分散）を検査する形へ書き換えた。区間を変えても分散が変わらないこと、
同じ seed で同じ列になること（呼び出し回数を揃えて比べる）を見る。

増分の源はスケジューラに残るので、`generate` のたびに `noise_sampler = None` へ
戻す。戻さないと同じ seed でも 2 回目から別の音になる（seed 決定論の破れ）。

### sfx のプロンプトは羅列でも動く（bgm とは逆）

bgm では属性の羅列が弱いと分かったので、sfx の Rule プロンプト（`event` `material`
`distance` `intensity` を並べたもの）も同じ欠陥を疑った。6 種 × 2 腕（Rule /
こちらで書いた説明文）を 20 ステップで回した：

| 種 | Rule の読み | 説明文の読み |
| --- | --- | --- |
| スイッチ | 1 打・立ち上がり 12ms・減衰 23ms・重心 11.7kHz（クリック） | 打なし・重心 2.3kHz・低域 −6dB（鈍い音） |
| グラス | 9 打（破片が散る） | 4 打 |
| ドア | 重心 231Hz | 重心 75Hz（亜低域の唸り） |
| 紙・足音 | ほぼ同じ（重心 4.4k / 4.3k、打 6 / 5） | 同じ |
| 雷 | 重心 103Hz・低域 −0.1dB | 重心 58Hz |
| 判定 | **Rule が同等以上**（勝ち 2・同等 3・負け 0） | — |

sfx の Rule プロンプトは「何が鳴るか」を主語にした句なので、説明文と同じ働きをする。
bgm のような書き換えはしない。

### bgm の明るさは楽器名の具体度で決まる

`strings` だけを名指すと低弦の唸りになり、2kHz 以上が −46 dB まで落ちる。同じ seed・
同じ尺で `violins and cello` と名指すと高域 −6.4 dB・重心 1018 Hz まで戻った。
`pad` は `with air and shimmer` を足しても −60 dB のままで、musicgen-small は
明るいパッドを出さない。規則は変えず、`probe` の `no_highs` を目印にする。

### Mix（重ね合わせ・ducking）
`engine/mix.py` に `overlay`（時刻と利得で重ねる）と `duck`（声の 5ms 包絡が
閾値を超えた分だけ bed を沈める）を足し、`bin/mix.py` で 3 層
（bed / voice / hit）を 1 本にする。天井は最後に一度だけ掛ける——重ねる途中で
切ると歪みが仕様になる。LUFS マスター正規化は将来スコープ。

実測（`examples/mixed-scene/scene-drop.wav`・14 秒・9 ステム）：ducking は声の鳴って
いる標本に限ると bed が 8.0 / 8.3 / 7.8 dB 沈み（3 つの声）、声の無い区間は 0.0 dB
（素通し）。声の区間のミックス RMS は声そのものの RMS と同じ（−15.0 / −16.4、
−15.0 / −15.3、−17.1 / −17.1 dB）ので、声は埋もれていない。

最初の版は全ステムを mono へ落としてから重ねていた。これは probe の欠陥 3 と同じ形で、
左右の相関が低い sfx ほど小さくなる（`glass-break` −1.3 dB・`gravel-steps` −2.1 dB）。
出力をステムの最大チャンネル数へ揃える形に直した：mono の声は両耳へ複製（真ん中）、
ステレオの sfx は左右を保つ。この場面は bed と声が主なので側（L−R）/2 は全体 −50.6 dB・
ガラスの区間 −43.8 dB と小さいが、sfx の広がりは消えずに残る。

この例の `mix.yaml` は最初、隣に無いステム（`s-door.wav` など）を指していて、
README のとおりに実行すると `mix: ファイルが無い` で落ちた。実体は `../sound-samples/` と
byte-identical だったので、参照先をそちらへ向けて二重に置くのをやめた。

### 測り器の欠陥 3（モノラルへ落として量を測っていた）
`peak` / `rms_db` / `clipped` をモノラル（左右の平均）で測っていた。左右の相関が低い
sound は平均で打ち消し合うので、ファイルの量でない数が出る。実測：sfx 6 本のうち
`glass-break`（相関 0.49）は peak 0.95 を **0.69** と報告し、RMS を 1.3 dB 低く、
`gravel-steps`（相関 0.25）は RMS を 2.1 dB 低く報告していた。しかも `normalize` は
天井 0.95 へ合わせており、全 6 本が実際は 0.950 で揃っていた——モノラル読みの peak
（0.69 / 0.73 / 0.94）は「天井に届いていない」と読める数だった。量は全チャンネル、帯域・重心・無音率・起伏は
モノラルで測る形に直した。逆相ステレオを無音と読まない検査を足した。

### 再生成の再現性（`provider_settings`）
`params.yaml` に Provider のサンプリング設定を残す。stable_audio の `steps` は品質と
時間を決めるが Spec に入らないので、保存しないと「同じ params から同じ音」が崩れる。
musicgen は `tokens`（尺を秒でなくトークン数で丸める）と `guidance_scale` を残す。

## 2026-08-29 — 実装一式（M0〜M3・資材分離・参照音声拡充）

### M0 — Provider スパイク（Tsukasa_Speech 確定）

- 作業ディレクトリ `/Users/user/sonic-loom-spike/`（venv=kokoro/chatterbox、venv_tsukasa=tsukasa）。
- Kokoro = 速度のみ・感情なし（切り捨て）。Chatterbox = exaggeration で強度反映（5 修正要）。
- **Provider は Tsukasa_Speech に確定**（ユーザー聴取で「圧倒的にいい」）。KotoDama プロンプト（自然言語の演技指示）→ 256 次元スタイル（timbre 128 + prosody 128）。
- **参照音声なしでも演技指示だけで声を生成できる**ことを実証（経路B）。
- モデル ~5GB（Top_ckpt 2GB / PLBERT 1.9GB / KTD 640MB）。日本語は `phonemize`（cutlet 経由）必須。
- 核心検証：抽象的 subtext 文の追記は破綻するが、subtext を具体的な抑揚指示（語尾の上げ下げ・ためらい・平坦）に変換する Resolve 経路なら明確に音に乗る（f0 実測：resolve_afraid 語尾上昇/mean325Hz vs resolve_indifferent 語尾下降/mean285Hz）。
- 声アイデンティティの制約：KotoDama プロンプト経路は女性バイアスが強い。
- 参照音声ライブラリ（老若男女 10 名）構築：VCTK（CC BY 4.0）若〜壮年 8 名 + Common Voice（CC0）老人 2 名。
- alpha/beta スイープで**確定 alpha=0.35, beta=0.7**（beta は「ピッチ演技のノブ」）。
- 複製 f0 の run 間分散は seed 固定で解決。境界話者 4 名は話者別 seed（`seeds.json`）で永続化。

### M1 — ウォーキングスケルトン

- 新リポジトリ `semantic-audio-loom/`（旧名 Sonic Loom。ブランド重複で改名）。7 段フロー（Validate → Route → Resolve → Generate → Normalize → Tag → Store）の Resolve 以外をつなぐ。
- パッケージ `semantic_audio_loom/`（config / types / providers / engine / skills）+ bin/（generate / regenerate）。
- E2E 実測：generate→regenerate で byte-identical（seed=42）。

### M2 — Resolve（価値の核心）

- LLM 呼び出しは SDK でなく stdlib urllib の直接 HTTP（anthropic 1.2.0 が temperature 引数を廃止して破綻したため）。`llm/client.py` が `/v1/messages` を直接叩く。
- Resolve の実体：subtext を抽象文でなく具体的な抑揚指示へ変換。Performance Spec に `prosody.intonation`（rising/falling/flat/wavering/neutral）を**スキーマ拡張で追加**。
- LLMResolver（既定）と RuleResolver（決定的写像・intonation=neutral・フォールバック）。
- M2 実測：同一台詞・同一 Direction で State だけ変えると Spec が変わる（返事が怖い→wavering vs どうでもいい→flat）。

### M3 — 一貫性検証

- mashiro を 2 シーン（朝 joy / 夜 anxiety）で生成、同一参照音声・同一キャラで f0 307.9Hz / 261.6Hz（差 46Hz は感情プロソディ、timbre は同一）。

### 資材の分離（ユーザー要望「キャラを再利用したい」）

- Step1 キャラ作り（`bin/character.py` → `characters/*.voice.yaml`）と Step2 声の生成（`bin/generate.py --character` → `projects/*/assets/`）を分離。
- 修正：resolve_rule が未指定 delivery を None で含めてスキーマ検証に落ちるバグを `_strip_none` で解決。

### 演技の振り付けと参照音声拡充（ユーザー要望）

- **演技資材**（`performances/*.direction.yaml`）：感情・声量・速度・delivery などの Direction を名前で再利用。`bin/performance.py`（init/validate/list）＋ `bin/generate.py --performance <name>`（CLI フラグで上書き）。
- **参照音声拡充**（`bin/reference.py`）：`synthesize`（ローカル生成・経路B・`--character` で voice.yaml の属性を入力）と `add`（著作権フリー音源の出典・ライセンス付き登録）。generate.py は既定で参照音声の欠落を検査し案内する。
- schemas 5 本化（performance_asset 追加）。

### 参照音声ライブラリを repo 内へ移設

- 以前は `資料/音声素材エンジン_構想/参照音声ライブラリ`（絶対パス）を config が参照していたが、clone で動かないため repo 直下 `references/` に本体（10 WAV + manifest.json + seeds.json）を移設。config.REFERENCE_LIB を repo 相対に変更。
- `requirements.txt` 追加。資料/側は検証産物（cloned/sweep/seed_sweep）だけ残す。

### リポジトリ構成の Claude Code 準拠

- 兄弟リポジトリ（elevate / distill-essence 等）の流儀に合わせ、CLAUDE.md / HISTORY.md / docs/ / skills/ / install.sh / .claude-plugin/ / .claude/skills（symlink）を整備。README は現行情報のみにスリム化し、履歴は HISTORY.md・深掘りは docs/ へ分離。
- 生成サンプルを `output*`（gitignore 済みスクラッチ）から `examples/mashiro-night/`（コミット対象）へ統合。

## 2026-08-29 — M4 蒸留（大量インプット → 資材）

- 手で埋める init の代わりに、物語・脚本・人物描写からキャラ（voice_profile）と演技（performance_asset）を自動生成する蒸留機構を追加。distill-essence-engine の蒸留（①理解→②選択→③翻訳）を音声資材向けに翻案。
- 二モード：`batch`（物語1つ → キャラ複数 × 演技複数）と `character`/`performance`（1入力 → 1資材）。`--synthesize` で元音声（経路B）も生成・登録、`--dry-run` で YAML 確認。
- ③翻訳の出力は schema の enum 制約（`pitch: very_low〜very_high` 等）。enum 外・必須欠落は手で直さず再生成（`_distill` が最大 3 回再試行）。
- `synthesize` の実体を `skills/reference.py` の `synthesize_reference` / `duration_sec` へ抽出し、`bin/reference.py` と `bin/distill.py` で共用。
- tests/ 新設（`test_distill.py`・モック LLM・10 件）+ conftest.py + requirements.txt に pytest 追加。

## 2026-08-29 — Asset Type 正典化（構想 §4 の 5 種）

- 音を声に閉じないよう、構想 §4 の 5 Asset Type（voice / bgm / ambience / sfx / foley）を正典として明文化。`types.ASSET_TYPES`（定数）＋ `schemas/asset_type.schema.json`（enum）＋ `validate_intent` の enum 外拒否で、将来スコープを閉じない。
- 実装済みは Phase 1 の `voice` のみ。ambience/sfx（Phase 2）・bgm（Phase 3）は将来スコープで、生成モデル・Resolve 経路・Sound Bible は未実装。詳細は docs/asset-types.md。

## 2026-08-29 — 多言語化（i18n / en・ja・zh）

- CLI 文言と LLM プロンプトを 2 層（`locales/{lang}.json` ＋ `prompts/{lang}.json`）で現地化。対象 en/ja/zh、既定 ja。言語解決は `--lang` > `SAL_LANG` > ja（未対応言語は警告して ja へ）。新規文言は `semantic_audio_loom/i18n.py` の `_t()`（引数名 `name`・`default` は日本語の安全弁）で解決。
- 固定列挙値（enum）は英語のまま、自由テキスト（situation/subtext/キャラ表示名）は `--lang` の言語で出力（プロンプト末尾に出力言語ディレクティブ）。台詞（`--line`）は Tsukasa が日本語 TTS のため常に日本語（領域事実＝i18n 対象外）。
- エンジン結線：resolve / distill / llm.client / engine に `lang` を追加。波括弧衝突回避のため、JSON スキーマ例を含む system プロンプトは `.format()` せず、`.format()` するのは `resolve.user` と `distill.retry` のみ。
- **経緯**：当初は並列リポジトリ（wisdom/elevate）と同じ「フル3層（locales+prompts+docs ミラー・既定 en）」を検討したが、(1) Tsukasa が日本語 TTS のため音声出力は日本語のまま＝非日本語話者が主対象になる可能性が低く docs 翻訳の実利が薄い、(2) 既定 en だと日本語 README と CLI 出力が非整合——の2点から「プロンプト＋CLI のみ・既定 ja・README/docs は日本語のまま」に絞った。docs ミラーツリーは作らない。
- tests/test_i18n.py 追加（言語解決の優先順位・3言語キー整合・en/zh プロンプトに日本語かな漏れなし・モック LLM で3言語完走・CLI `--lang` スモーク）。テスト 24 件。

## 2026-08-30 — 語尾の「ぶった斬れ」対策（末尾フェード）

- 実測：Tsukasa の拡散出力は release を持たない音素（「る」「た」などの短母音・促音系）だと
  最終フレームを有声のまま終端させる（末尾 RMS 0.16〜0.27・decay 0ms）。長母音
  （「う」「い」）は自然減衰（decay 500〜620ms）。要の一打は文末＝切断位置に置かれるため、
  重要な語ほど「余韻がぶった斬れる」。
- B（余韻の回復）は不発：`rate_of_speech` を 1.0→0.75 に下げても decay は 0ms のまま。
  `intonation=falling`（"trailing off" 追加）も sadness 感情句に既に含まれており変化なし。
- 方針 A（末尾フェード）で確定：`normalize` に半ハン余弦フェード（`TAIL_FADE_MS=30ms`）を
  追加。クリック除去に留め、余韻そのものは復元しない（モデルが release を出さないため）。
  自然減衰した波形（末尾無音）には実質 no-op。
- tests/test_normalize.py 追加（3件）。

## 2026-08-30 — 読み（ふりがな）の指定（漢字の誤読対策）

- 実測：Tsukasa の phonemize（cutlet / UniDic）が「既読」を `kijomi`（きよみ）と誤読する。
  `phonemize('既読') => kijomi`、かな読み `phonemize('きどく') => kidokɯ` は正しい。
  つまり、かなを渡せば正しく発音される（漢字→かな変換だけが誤読の原因）。
- 対処：`--line` 内に `漢字《かな》` のふりがなを指定できるようにした。`parse_ruby`
  （`semantic_audio_loom/text.py`）が台詞を（表示用台詞, 読み）に分解し、プロバイダは
  `reading` があればそれを phonemize、無ければ台詞をそのまま phonemize（従来どおり）。
  保存される台詞（dialogue）は `《》` を外した綺麗な文。`reading` は params.yaml に保存し
  regenerate が再現する。
- 入力 UI はふりがな《》記法のみ（`--reading` フラグは追加しない、ユーザー確認済み）。
  未アノテーションの漢字は従来どおり cutlet が読む。
- 新設: `semantic_audio_loom/text.py`（parse_ruby）、`tests/test_text.py`（4件）。

## 2026-08-30 — キャラ名の自動ふりがな（name_reading）

- 実測：語りサンプルで「真白」が `maʔɕiɽo`（まっしろ＝普通名詞「真っ白」）と誤読された。
  固有名詞の誤読は手書き《》で都度直すには漏れやすく、特にナレーション（話者＝語り）では
  本人でないキャラ名が台詞に頻出する。
- 対処：`characters/*.voice.yaml` に `name_reading`（キャラ表示名の読み）を追加。`build_intent`
  が全キャラの `name_reading` をレジストリ化し、台詞中のキャラ名へ `annotate_reading`
  （`text.py`、既アノテーションをスキップして `漢字《かな》` を挿入）で自動ルビを振る。
  手書き《》と自動ふりがなは共存し、両方とも `reading` へ反映される。
- `mashiro.voice.yaml` に `name_reading: ましろ` を追加（真白→まっしろ誤読への対処）。
  語りサンプル（opening / refrain / ending）を再生成し、`reading` に「ましろ」が入ることを
  params.yaml で確認。
- 新設: `text.py` に `annotate_reading`、`tests/test_text.py`（+3件）、`tests/test_character_voice.py`（3件）。

## 2026-08-30 — Scene / Timeline（複数人物 × 間の合成）

- 動機：`bin/generate.py` が「1 キャラ × 1 台詞 → 1 WAV」に閉じ、真白・ニジ・語りを
  「一つの場面（余白含む）として 1 WAV に複数人物を登場させる」ことができなかった。
  外部 DAW 合成だと間のタイミングが DAW プロジェクトに閉じ、seed決定論（再生）が壊れる。
- 設計：scene は voice の 7 段フローの外側に置く合成レイヤ。`scene.yaml`（宣言的な源）が
  キュー（キャラ＋台詞＋Direction＋pause_before）を宣言し、各キューを既存 voice 生成で
  作って無音（間）で連結する。scene は 5 Asset Type の正典に加えない（voice の合成）。
- 「間（余白）」＝無音（秒）。`pause_before`（個別）と `default_pause`（既定）。既存
  `performance_direction.schema.json` に予約済みだった `pause_before` の語彙を採用。
- 再現性：render が seed を採番して `scene.params.yaml` の `parameters.cues` に各キュー
  の resolved Spec（voice_profile / performance_spec / dialogue / reading / seed）＋
  pause_before を記録。`bin/scene.py --params` が `generate_request`（LLM なし）で
  byte-identical に再生成。
- 環境音・BGM・ducking・パン・クロスフェード・LUFS マスターは将来スコープ（Phase 4 の残り）。
- 新設: `engine/mix.py`（silence/mix_cues）、`scene.py`（load_scene/cue_from_params）、
  `schemas/scene.schema.json`、`bin/scene.py`、`tests/test_mix.py`（6件）、`tests/test_scene.py`（7件）。
  `types.py` に SceneCue/Scene、`engine/validate.py` に validate_scene、locales ×3 に scene。

## 2026-08-30 — 省略記号「…」が「へぇ」に化ける問題の対処

- 実測：scene 例の真白の台詞「……まだ、起きてる？」が「へぇ…まだ、起きてる？」と聞こえる。
  原因は Tsukasa の phonemize（cutlet）が「…」をドット列に変え（`……まだ` → `...... mada`）、
  モデルがそのドット列を有声（「へぇ」様）に読み上げること。構造化ポーズ（間）は非対応。
- 対処：`text.py` に `normalize_ellipsis` を追加し、phonemize の**入力だけ**を正規化する。
  文頭・文末の「…」は除去（間は scene の `pause_before` や emotion/delivery が担う）、
  文中の「…」は「、」に置換（ポーズ境界）。台詞（dialogue）自体は変えない＝表示・
  params.yaml は従来どおりで、seed決定論（再生成）も保たれる。
- 適用先は `providers/tsukasa.py` の `generate`（`request.reading or dialogue` を
  正規化してから phonemize）。`tests/test_text.py` に +5 件。
