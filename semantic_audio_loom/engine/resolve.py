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

from semantic_audio_loom import i18n
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


def resolve_llm(intent: GenerationIntent, lang: str | None = None) -> dict:
    from semantic_audio_loom.llm.client import ClaudeClient

    prompts = i18n.load_prompts(lang)
    client = ClaudeClient()
    system = prompts["resolve"]["system"]
    user = _user_prompt(intent, prompts)
    return _strip_none(client.complete_json(system, user))


def resolve(intent: GenerationIntent, mode: str = "llm", lang: str | None = None) -> dict:
    if mode == "rule":
        return resolve_rule(intent)
    try:
        return resolve_llm(intent, lang=lang)
    except Exception as exc:  # 認証不可・ゲートウェイ障害・JSON 解釈失敗など
        print(
            i18n._t(
                i18n.load_locale(lang),
                "resolve",
                "fallback",
                "[resolve] LLM に失敗したため Rule へフォールバック: {exc}",
                exc=exc,
            ),
            file=sys.stderr,
        )
        return resolve_rule(intent)


def _strip_none(spec: dict) -> dict:
    """トップレベルの None 値を落とす（省略可能な enum フィールドを None で
    含めるとスキーマ検証に落ちるため。LLM が null を返しても通す）。"""
    return {k: v for k, v in spec.items() if v is not None}


def _user_prompt(intent: GenerationIntent, prompts: dict) -> str:
    emotion = intent.emotion or {}
    performance = intent.performance or {}
    state = intent.character_state or {}
    scene = intent.scene or {}
    r = prompts["resolve"]
    none = r["none"]
    subtext_section = (
        r["subtext_given"].format(subtext=intent.subtext)
        if intent.subtext
        else r["subtext_infer"]
    )
    return r["user"].format(
        dialogue=intent.dialogue,
        situation=intent.situation or none,
        scene=json.dumps(scene, ensure_ascii=False) if scene else none,
        state=json.dumps(state, ensure_ascii=False) if state else none,
        emotion=emotion.get("primary", "neutral"),
        intensity=emotion.get("intensity", "none"),
        volume=performance.get("volume", "normal"),
        speed=performance.get("speed", "natural"),
        pitch=performance.get("pitch", "natural"),
        delivery=performance.get("delivery", "") or none,
        subtext_section=subtext_section,
    )
