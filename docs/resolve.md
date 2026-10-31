# Resolve — subtext を音に乗せる（M2 の核心）

## 何をするか

Direction（監督＝意図）と State / Scene / Dialogue を LLM が解釈し、
**Performance Spec**（俳優＝実現）へ解決する。

```
Direction + State + Scene + Dialogue  →  LLM  →  Performance Spec
```

## なぜ必要か（M0 実測の核心）

subtext（台詞の裏の意味）は**抽象文のままでは音に乗らない**。

- 抽象 subtext 文をそのままプロンプトへ追記しても破綻（beta を上げても無効）。
- subtext を**具体的な抑揚指示**（語尾 intonation）へ変換すれば明確に音に乗る。

f0 実測（同一台詞・同一 Direction・State のみ変更）：

| 状態 | subtext | intonation | mean f0 |
| --- | --- | --- | --- |
| 返事が怖い | 返事が怖いが、繋がりを求めてしまう | wavering（語尾上昇） | ~325Hz |
| どうでもいい | （なし） | flat（語尾下降） | ~285Hz |

⚠️ この 40 Hz は **intonation の語の効きではない**。同じ 2 語を State まで固定して
振ると差は 4.4 Hz（291.4 対 287.0）で、語尾の傾きも名前どおりにならない
（`projects/longform/acting-inton-070/`）。**動いていたのは state の側**である。

## 実装

- **LLMResolver**（既定）：`llm/client.py` が `/v1/messages` を直接叩く（SDK 不使用。anthropic 1.2.0 が temperature 引数を廃止して破綻したため stdlib urllib に移行）。
- **RuleResolver**（`--resolve rule`）：決定的写像。intonation=neutral 固定。LLM 失敗時のフォールバック。
- Performance Spec の `prosody.intonation`（rising / falling / flat / wavering / neutral）はスキーマ拡張で追加（M0 で語尾が音に乗ることを確認済みのため）。

## Spec の語彙

- Direction の `intensity`（none/subtle/moderate/strong/overwhelming）は Resolve が実数 0.0〜1.0 へ解決。
- Provider（Tsukasa）が反映できる controls（emotion / delivery / 声量 / 速度 / 語尾）だけを KotoDama 散文へ変換する。emphasis / breath / pauses の構造化制御は共通欠落。

## 一貫性（M3）

同一参照音声（`female_young_p308`）・同一キャラでシーンを変えても、f0 差は感情プロソディの範囲（朝 joy 307.9Hz / 夜 anxiety 261.6Hz）で、timbre は同一に保たれる。

## どの欄が、声を動かすか

Direction の欄は語の数が欄ごとに違うが、**声に届く段の数は語の数と対応しない**。
同じ行・同じ seed で欄だけを振った実測（`projects/longform/acting-*/`・
`projects/longform/REPORT.md`「Direction の欄は、どれが段になるか」）。

| 欄 | 語 | 声に届く段 | 何が動くか |
| --- | --- | --- | --- |
| `speed` | 5 | **5**（単調・1.74〜1.80 倍・3 感情とも） | 長さ（両端で高さも +15 Hz） |
| `emotion` | 11 | 効く（neutral より +4〜+26 Hz。**隣どうしは同じ声**） | 高さ・長さ・抑揚（`acting-emotion-ladder/`） |
| `pitch` | 6 | 2〜3（**下だけ**。very_low・low が同じ段） | 高さ（上がる語は無い・`acting-pitch-ladder/`） |
| `intensity` | 5 | 2（`subtle`＝`moderate`、`strong` で跳ねる） | 高さ・長さ |
| `delivery` | 12 | 3（`flat`・`cold` が下、`aggressive`・`desperate` が上、残り 8 語は同じ） | 高さ・長さ |
| `intonation` | 5 | ほぼ 0（語の幅 7.7 Hz 対 seed の幅 74〜87 Hz） | 語尾の傾きもラベルに従わない |
| `breathiness` | 4 | 2（幅が小さい） | 有声の割合・高域 |
| `volume` | 5 | **0**（声の大きさとしては） | energy は動かない（shout だけ f0 +9.6・長さ +0.13 秒）。ミックスの `gain_db` が作る |

- **演じ分けの土台は `speed`。** 5 語が単調に並ぶ唯一の欄。joy・anger・sadness の
  3 感情 × seed 5 で、すべての seed が同じ順序になる。長い行（24 文字）でも 1.75 倍で
  5/5 単調。**高さも短い行の両端で +15 Hz 開く**（306.0 → 320.8 Hz・seed 4/5。
  長い行では動かない）。
- **2 つの欄を同時に振ると、上へ動かす型だけが埋まる。** `speed` を端まで振ると
  `aggressive` の +6.7 Hz が 0 になる（`acting-knob-stack/`）。**下へ動く `cold` / `flat`
  は端でも残り**（−9〜−11 / −17〜−21 Hz・`acting-knob-stack-cold/`）、`pitch` を振ると
  半分残る（+6.8 → +3.4 / +2.1 Hz・`acting-knob-stack-pitch/`）。
  **aggressive は `speed: natural` で使う。**
- **強い欄どうしも足し算にならない。** `speed` の高さの効きは `pitch: low` で 0.5 Hz に
  なる（natural +4.3・high +5.9 Hz・`acting-knob-stack-speed-pitch/`）。**長さは動く。**
  この条件では `pitch` の `high` は効かず（−0.1 Hz）、`low` だけが段になる（−13.5 Hz）。
- **感情は neutral から上へは動くが、感情どうしは書き分けられない。** 11 語 × seed 5
  （`acting-emotion-ladder/`）：neutral との差は +4（sadness）〜+26（fear）Hz で、
  9/10 が 5/5。だが**離れるのは遠い 2 語だけ**（fear − sadness +21.3 Hz・5/5）で、
  fear − joy +1.6・confidence − anxiety +0.1 Hz は同じ声。**seed の散らばり（65〜98 Hz）が
  感情の差より大きいので、1 本ずつ聞いて感情を当てることはできない。**
- **強弱を `intensity` の書き分けで作らない。** `subtle` と `moderate` は同じ音になる。
- **`delivery` の真ん中 8 語（gentle / cheerful / hesitant / restrained / subtle /
  suppressed / intimate / controlled）は、書き分けても同じ声になる。** 動くのは `aggressive`・
  `desperate`（上へ +7〜+8 Hz）と `cold`・`flat`（下へ −9・−18 Hz）の 4 語だけ。
- **声量は声ではなくミックス。** 生成された声はどれも peak 0.95 に揃い、
  レベル差は残らない（`assemble.py` の `VOLUME_GAIN`）。`shout` は 5 語で唯一
  f0 +9.6 Hz・長さ +0.13 秒を動かすが、**energy は 0.6 dB 下がる**。
- **`intonation` の 5 語は、実質同じ声。** 語尾の傾きは名前のとおりにならない
  （rising は最大にならず、wavering が最大）。床（beta 0.0）でのみ
  ラベルどおりの順になるが、どの語も大きく上向きで差は 0.95 半音/秒。
  **M0 で見た 40 Hz の差は、語ではなく state の側の差だったと読める。**
- `breathiness` と `volume` で囁きを作ることはできない。息は `voice_fx` の帯域で作る。
