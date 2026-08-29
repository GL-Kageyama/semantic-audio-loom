"""蒸留（distill）＝大量のインプットを再利用資材へ折りたたむ（M4）。

distill-essence-engine の「蒸留」（①理解→②選択→③翻訳）を音声資材向けに翻案したもの。
物語・脚本・人物描写から、再利用資材（キャラ＝voice_profile / 演技＝performance_asset）を
自動生成する。画像蒸留との違いは出力先：ここでは ③翻訳 が schema の enum 制約を持つ
構造化 JSON に落ち、validate を通ったものだけを characters/ ・ performances/ に書く。

二モード：
- batch    … 物語テキスト1つ → 主要キャラ複数 × 代表シーン複数
              （distill_characters / distill_performances）
- single   … 1入力 → キャラ1体（distill_character）または演技1つ（distill_performance）

LLM は Resolve と同じ ClaudeClient（llm/client.py）。崩れた JSON や enum 外は
手で直さず再生成する。
"""
from __future__ import annotations

import os
import re

from semantic_audio_loom import config
from semantic_audio_loom.engine import validate

# schemas/voice_profile.schema.json / performance_asset.schema.json の enum と一致させる。
# ここを増やすときはスキーマ側も合わせる。
VOICE_ENUMS = {
    "age": {"child", "adolescent", "young_adult", "adult", "middle_aged", "elderly"},
    "gender": {"female", "male"},
    "pitch": {"very_low", "low", "medium_low", "medium", "medium_high", "high", "very_high"},
    "texture": {"soft", "warm", "clear", "bright", "dark", "husky", "breathy", "neutral"},
    "breathiness": {"none", "slight", "moderate", "heavy"},
    "resonance": {"intimate", "chest", "head", "nasal", "bright", "neutral"},
}
PERF_ENUMS = {
    "emotion": {"anxiety", "sadness", "anger", "fear", "joy", "confidence", "loneliness",
                "excitement", "calm", "guilt", "neutral"},
    "intensity": {"none", "subtle", "moderate", "strong", "overwhelming"},
    "volume": {"whisper", "quiet", "normal", "loud", "shout"},
    "speed": {"very_slow", "slow", "natural", "fast", "very_fast"},
    "pitch": {"very_low", "low", "slightly_low", "natural", "slightly_high", "high"},
    "breathiness": {"none", "slight", "moderate", "heavy"},
    "delivery": {"restrained", "subtle", "suppressed", "controlled", "flat", "gentle",
                 "intimate", "aggressive", "cheerful", "cold", "desperate", "hesitant"},
}

_SYSTEM_CHARACTERS = """あなたは音声キャラクターの蒸留器（Distiller）です。与えられた物語・脚本・人物描写から、
登場人物の「声の本質」を蒸留してください。

①理解：各登場人物の声質（年齢・性別・ピッチ・声の質感・息の量・共鳴）と話し方の描写を掴む。
②選択：全員ではなく「主要な」登場人物だけを選ぶ（目安 5 人以内）。脇役・一言だけの人物は省く。
③翻訳：声質の描写を、以下の enum に必ず収めて翻訳する（enum 外の値を出さない）。

JSON スキーマ（準拠必須）:
{
  "characters": [
    {
      "name": "<ローマ字スラッグ（例: mashiro）>",
      "character": "<表示名（日本語可）>",
      "voice": {
        "age": "<child|adolescent|young_adult|adult|middle_aged|elderly>",
        "gender": "<female|male>",
        "pitch": "<very_low|low|medium_low|medium|medium_high|high|very_high>",
        "texture": "<soft|warm|clear|bright|dark|husky|breathy|neutral>",
        "breathiness": "<none|slight|moderate|heavy>",
        "resonance": "<intimate|chest|head|nasal|bright|neutral>"
      }
    }
  ]
}

制約：
- age / pitch / texture / breathiness は必須。gender / resonance もできるだけ推定する。
- name は半角英数字とハイフンのみ。
- JSON のみを返す（説明文・Markdown フェンスは付けない）。"""

_SYSTEM_CHARACTER = """あなたは音声キャラクターの蒸留器（Distiller）です。与えられた人物描写から、
1 人の「声の本質」を蒸留してください。

①理解：その人物の声質（年齢・性別・ピッチ・声の質感・息の量・共鳴）を掴む。
②翻訳：声質の描写を、以下の enum に必ず収めて翻訳する（enum 外の値を出さない）。

JSON スキーマ（準拠必須）:
{
  "character": "<表示名（日本語可）>",
  "voice": {
    "age": "<child|adolescent|young_adult|adult|middle_aged|elderly>",
    "gender": "<female|male>",
    "pitch": "<very_low|low|medium_low|medium|medium_high|high|very_high>",
    "texture": "<soft|warm|clear|bright|dark|husky|breathy|neutral>",
    "breathiness": "<none|slight|moderate|heavy>",
    "resonance": "<intimate|chest|head|nasal|bright|neutral>"
  }
}

制約：
- age / pitch / texture / breathiness は必須。gender / resonance もできるだけ推定する。
- JSON のみを返す（説明文・Markdown フェンスは付けない）。"""

_SYSTEM_PERFORMANCES = """あなたは音声演技の蒸留器（Distiller）です。与えられた物語・脚本から、
代表的な「演技シーン」を蒸留してください。

①理解：シーンごとの感情・状況・台詞・裏の意味（subtext）を掴む。
②選択：全シーンではなく、感情が際立つ代表的な数シーンを選ぶ（目安 6 つ以内）。
③翻訳：各シーンを、以下の enum に必ず収めて翻訳する（enum 外の値を出さない）。

JSON スキーマ（準拠必須）:
{
  "performances": [
    {
      "name": "<ローマ字スラッグ（例: anxious-night-call）>",
      "emotion": "<anxiety|sadness|anger|fear|joy|confidence|loneliness|excitement|calm|guilt|neutral>",
      "intensity": "<none|subtle|moderate|strong|overwhelming>",
      "volume": "<whisper|quiet|normal|loud|shout>",
      "speed": "<very_slow|slow|natural|fast|very_fast>",
      "pitch": "<very_low|low|slightly_low|natural|slightly_high|high>",
      "breathiness": "<none|slight|moderate|heavy>",
      "delivery": "<restrained|subtle|suppressed|controlled|flat|gentle|intimate|aggressive|cheerful|cold|desperate|hesitant>",
      "situation": "<そのシーンの状況を一言で>",
      "subtext": "<台詞の裏の意味を一言で>"
    }
  ]
}

制約：
- emotion は必須。situation / subtext は必ず埋める（Resolve の入力になる）。
- name は半角英数字とハイフンのみ。
- JSON のみを返す（説明文・Markdown フェンスは付けない）。"""

_SYSTEM_PERFORMANCE = """あなたは音声演技の蒸留器（Distiller）です。与えられたシーン・台詞の描写から、
1 つの「演技」を蒸留してください。

①理解：そのシーンの感情・状況・台詞・裏の意味（subtext）を掴む。
②翻訳：シーンを、以下の enum に必ず収めて翻訳する（enum 外の値を出さない）。

JSON スキーマ（準拠必須）:
{
  "emotion": "<anxiety|sadness|anger|fear|joy|confidence|loneliness|excitement|calm|guilt|neutral>",
  "intensity": "<none|subtle|moderate|strong|overwhelming>",
  "volume": "<whisper|quiet|normal|loud|shout>",
  "speed": "<very_slow|slow|natural|fast|very_fast>",
  "pitch": "<very_low|low|slightly_low|natural|slightly_high|high>",
  "breathiness": "<none|slight|moderate|heavy>",
  "delivery": "<restrained|subtle|suppressed|controlled|flat|gentle|intimate|aggressive|cheerful|cold|desperate|hesitant>",
  "situation": "<そのシーンの状況を一言で>",
  "subtext": "<台詞の裏の意味を一言で>"
}

制約：
- emotion は必須。situation / subtext は必ず埋める（Resolve の入力になる）。
- JSON のみを返す（説明文・Markdown フェンスは付けない）。"""


def _check_enums(obj: dict, enums: dict) -> None:
    for key, allowed in enums.items():
        value = obj.get(key)
        if value not in (None, "") and value not in allowed:
            raise ValueError(f"enum 外の値: {key}={value!r}（許可: {sorted(allowed)}）")


def _check_voice(voice: dict) -> None:
    _check_enums(voice, VOICE_ENUMS)
    for req in ("age", "pitch", "texture", "breathiness"):
        if req not in voice:
            raise ValueError(f"voice.{req} がありません")


def _check_characters(data: dict) -> None:
    chars = data.get("characters")
    if not isinstance(chars, list):
        raise ValueError("'characters' が配列ではありません")
    for c in chars:
        if not isinstance(c, dict) or not c.get("name"):
            raise ValueError("キャラクターに name がありません")
        _check_voice(c.get("voice") or {})


def _check_character(data: dict) -> None:
    _check_voice(data.get("voice") or {})


def _check_perf_fields(p: dict) -> None:
    if not p.get("emotion"):
        raise ValueError("emotion がありません")
    _check_enums(p, PERF_ENUMS)


def _check_performances(data: dict) -> None:
    perfs = data.get("performances")
    if not isinstance(perfs, list):
        raise ValueError("'performances' が配列ではありません")
    for p in perfs:
        if not isinstance(p, dict) or not p.get("name"):
            raise ValueError("演技に name がありません")
        _check_perf_fields(p)


def _check_performance(data: dict) -> None:
    _check_perf_fields(data)


def _distill(system: str, user: str, expect_key: str | None = None, check=None, attempts: int = 3) -> dict:
    """LLM を呼んで JSON を得る。構造・enum が崩れたら再生成する（手で直さない）。"""
    from semantic_audio_loom.llm.client import ClaudeClient

    client = ClaudeClient()
    prompt = user
    for attempt in range(attempts):
        try:
            data = client.complete_json(system, prompt)
            if expect_key is not None and expect_key not in data:
                raise ValueError(f"応答に '{expect_key}' がありません")
            if check is not None:
                check(data)
            return data
        except Exception as exc:
            if attempt == attempts - 1:
                raise
            prompt = (
                user
                + f"\n\n（前回の出力が不正でした: {exc}。JSON のみを、schema の enum に収めて正しく返してください。）"
            )


def distill_characters(text: str) -> list[dict]:
    data = _distill(_SYSTEM_CHARACTERS, text, expect_key="characters", check=_check_characters)
    return data.get("characters", [])


def distill_performances(text: str) -> list[dict]:
    data = _distill(_SYSTEM_PERFORMANCES, text, expect_key="performances", check=_check_performances)
    return data.get("performances", [])


def distill_character(text: str) -> dict:
    return _distill(_SYSTEM_CHARACTER, text, check=_check_character)


def distill_performance(text: str) -> dict:
    return _distill(_SYSTEM_PERFORMANCE, text, check=_check_performance)


def slug(name: str) -> str:
    """資材名（ファイル名の接頭辞）を正規化する：小文字・非英数字→ハイフン。"""
    s = (name or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s or "unnamed"


def write_character(asset: dict, overwrite: bool = False) -> str:
    """蒸留したキャラを characters/<slug>.voice.yaml に書き、パスを返す。

    asset は {name, character, voice, reference_audio?}。schema 検証を通ったものだけ書く。
    """
    import yaml

    name = slug(asset.get("name") or "")
    profile = {
        "character": asset.get("character") or name,
        "voice": {k: v for k, v in (asset.get("voice") or {}).items() if v},
    }
    if asset.get("reference_audio"):
        profile["reference_audio"] = asset["reference_audio"]
    validate.validate_voice_profile(profile)
    os.makedirs(config.CHARACTERS_DIR, exist_ok=True)
    path = os.path.join(config.CHARACTERS_DIR, name + ".voice.yaml")
    if os.path.exists(path) and not overwrite:
        raise FileExistsError(f"{path} は既にあります（--overwrite で上書き）")
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(profile, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
    return path


def write_performance(asset: dict, overwrite: bool = False) -> str:
    """蒸留した演技を performances/<slug>.direction.yaml に書き、パスを返す。

    asset は {name, emotion, intensity, ..., situation, subtext}。schema 検証を通ったものだけ書く。
    """
    import yaml

    name = slug(asset.get("name") or "")
    direction = {k: v for k, v in asset.items() if k != "name" and v not in (None, "")}
    validate.validate_performance_asset(direction)
    os.makedirs(config.PERFORMANCES_DIR, exist_ok=True)
    path = os.path.join(config.PERFORMANCES_DIR, name + ".direction.yaml")
    if os.path.exists(path) and not overwrite:
        raise FileExistsError(f"{path} は既にあります（--overwrite で上書き）")
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(direction, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
    return path
