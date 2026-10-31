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
| `speed` | 5 | **5**（単調・1.74〜1.80 倍・3 感情とも） | 長さ |
| `emotion` | 11 | 効く（seed の振れより小さい） | 高さ・長さ・抑揚 |
| `pitch` | 6 | 2（`high` だけ離れる） | 高さ |
| `intensity` | 5 | 2（`subtle`＝`moderate`、`strong` で跳ねる） | 高さ・長さ |
| `delivery` | 12 | 2（`flat`・`cold` だけ下がる） | 高さ・長さ |
| `intonation` | 5 | ほぼ 0 | — |
| `breathiness` | 4 | 2（幅が小さい） | 有声の割合・高域 |
| `volume` | 5 | **0**（声としては） | 何も動かない（ミックスの `gain_db` が作る） |

- **演じ分けの土台は `speed`。** 5 語が単調に並ぶ唯一の欄。joy・anger・sadness の
  3 感情 × seed 5 で、すべての seed が同じ順序になる。動くのは発話の長さ（間の割合と
  高さは動かない）。
- **強弱を `intensity` の書き分けで作らない。** `subtle` と `moderate` は同じ音になる。
- **声量は声ではなくミックス。** 生成された声はどれも peak 0.95 に揃い、
  レベル差は残らない（`assemble.py` の `VOLUME_GAIN`）。
- `breathiness` と `volume` で囁きを作ることはできない。息は `voice_fx` の帯域で作る。
