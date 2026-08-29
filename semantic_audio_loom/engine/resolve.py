"""Resolve（7 段フローの第 3 段・M2 で追加）＝価値の核心。

Direction（監督＝意図）＋ State ＋ Scene ＋ Dialogue を、モデル非依存の
Performance Spec（俳優＝実現）へ解決する。

M0 で確定した Resolve の実体：
- subtext を「抽象文の追記」で渡しても音には乗らない（beta を上げても無効）。
- subtext を**具体的な抑揚指示（語尾の上げ下げ・ためらい・平坦）**へ変換して初めて乗る。
- よって LLM は subtext の推論だけでなく、それを Spec の prosody（特に
  `prosody.intonation`）へ具体化することを担う。

二実装：
- `LLMResolver` … 外部 LLM（Claude API）。既定。subtext を推論し Spec を具体化。
- `RuleResolver`  … 決定的な写像（LLM なし）。Direction をそのまま Spec へ移す。
                      subtext 推論・語尾 intonation は行わない（neutral 固定）。

`resolve()` は mode で切り替え、LLM 失敗時は Rule へフォールバックして
パイプラインを止めない（崩れた Resolve で全体を落とさない）。
"""
from __future__ import annotations

import json
import sys

from semantic_audio_loom.types import GenerationIntent

INTENSITY_MAP = {
    "none": 0.0, "subtle": 0.25, "moderate": 0.5, "strong": 0.75, "overwhelming": 1.0,
}
EFFORT_MAP = {
    "whisper": "relaxed", "quiet": "relaxed", "normal": "normal",
    "loud": "projected", "shout": "strained",
}


def resolve_rule(intent: GenerationIntent) -> dict:
    """決定的な写像。Direction を Spec へ素直に移す（語尾 intonation は neutral）。"""
    emotion = intent.emotion or {}
    performance = intent.performance or {}
    primary = emotion.get("primary", "neutral")
    intensity_enum = emotion.get("intensity", "none")
    spec = {
        "emotion": {
            "primary": primary,
            "intensity": INTENSITY_MAP.get(intensity_enum, 0.5),
        },
        "loudness": {"effort": EFFORT_MAP.get(performance.get("volume", "normal"), "normal")},
        "prosody": {
            "pace": performance.get("speed", "natural"),
            "pitch": performance.get("pitch", "natural"),
            "intonation": "neutral",
            "pauses": [],
            "emphasis": [],
            "breath": [],
        },
        "subtext": intent.subtext or "",
    }
    if performance.get("delivery"):
        spec["delivery"] = performance["delivery"]
    return spec


def resolve_llm(intent: GenerationIntent) -> dict:
    from semantic_audio_loom.llm.client import ClaudeClient

    client = ClaudeClient()
    system = _SYSTEM_PROMPT
    user = _user_prompt(intent)
    return _strip_none(client.complete_json(system, user))


def resolve(intent: GenerationIntent, mode: str = "llm") -> dict:
    if mode == "rule":
        return resolve_rule(intent)
    try:
        return resolve_llm(intent)
    except Exception as exc:  # 認証不可・ゲートウェイ障害・JSON 解釈失敗など
        print(f"[resolve] LLM に失敗したため Rule へフォールバック: {exc}", file=sys.stderr)
        return resolve_rule(intent)


def _strip_none(spec: dict) -> dict:
    """トップレベルの None 値を落とす（省略可能な enum フィールドを None で
    含めるとスキーマ検証に落ちるため。LLM が null を返しても通す）。"""
    return {k: v for k, v in spec.items() if v is not None}


def _user_prompt(intent: GenerationIntent) -> str:
    emotion = intent.emotion or {}
    performance = intent.performance or {}
    state = intent.character_state or {}
    scene = intent.scene or {}
    lines = [
        "以下の入力から Performance Spec を JSON で返してください。",
        "",
        f"台詞: {intent.dialogue}",
        f"状況: {intent.situation or '（なし）'}",
        f"シーン: {json.dumps(scene, ensure_ascii=False) if scene else '（なし）'}",
        f"キャラクター状態: {json.dumps(state, ensure_ascii=False) if state else '（なし）'}",
        "",
        "監督の演技指示（Direction）:",
        f"  主感情 emotion: {emotion.get('primary', 'neutral')}",
        f"  感情強度 intensity: {emotion.get('intensity', 'none')}",
        f"  声量 volume: {performance.get('volume', 'normal')}",
        f"  速度 speed: {performance.get('speed', 'natural')}",
        f"  ピッチ pitch: {performance.get('pitch', 'natural')}",
        f"  演技トーン delivery: {performance.get('delivery', '') or '（なし）'}",
    ]
    if intent.subtext:
        lines += ["", f"subtext（人間が指定・これを採用すること）: {intent.subtext}"]
    else:
        lines += ["", "subtext は入力の状況・状態・台詞から推論してください。"]
    return "\n".join(lines)


_SYSTEM_PROMPT = """あなたは音声演技の Resolver です。監督の意図（Direction）とキャラクター状態を、
モデル非依存の Performance Spec（JSON）へ変換してください。

最重要ルール：**subtext（台詞の裏の意味）は抽象文のままでは音に乗りません**。
必ず「具体的な抑揚指示」へ変換してください。特に文末の語尾（intonation）を
rising（上がる）/ falling（下がる）/ flat（平板）/ wavering（揺れる・ためらい）/ neutral
のどれかに具体化してください。例：「返事が怖い」という裏の意味なら、語尾が揺れる
（wavering）か、問いかけなら上がる（rising）。

以下は Performance Spec の JSON スキーマ（準拠必須）。

{
  "emotion": { "primary": "<anxiety|sadness|anger|fear|joy|confidence|loneliness|excitement|calm|guilt|neutral>",
               "intensity": 0.0 },      // 0.0〜1.0 の実数
  "loudness": { "effort": "<relaxed|normal|projected|strained>" },
  "prosody": {
    "pace": "<very_slow|slow|natural|fast|very_fast>",
    "pitch": "<very_low|low|slightly_low|natural|slightly_high|high>",
    "intonation": "<rising|falling|flat|wavering|neutral>",
    "pauses": [ {"after": "<語句>", "duration": 0.0} ],
    "emphasis": [ {"word": "<語句>", "strength": "<weak|medium|strong>"} ],
    "breath": [ {"at": "<語句>", "type": "<slight|moderate|heavy>"} ]
  },
  "delivery": "<restrained|subtle|suppressed|controlled|flat|gentle|intimate|aggressive|cheerful|cold|desperate|hesitant>",
  "subtext": "<台詞の裏の意味を一言で>"
}

制約：
- pauses / emphasis / breath は意味がある場合のみ記述し、なければ空配列 []。
- delivery は Direction の delivery があればそれを尊重し、なければ演技に合うものを選ぶ。
- emotion.primary と intensity は Direction と State を統合して決定する。
- JSON のみを返す（説明文・Markdown フェンスは付けない）。"""
