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
手で直さず再生成する。system プロンプトと再生成・エラー文言は prompts/{lang}.json で
現地化する（固定列挙値は英語のまま、自由テキストは --lang の言語で出力）。
"""
from __future__ import annotations

import os
import re

from semantic_audio_loom import config, i18n
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
    "intonation": {"neutral", "rising", "falling", "flat", "wavering"},
}


def _check_enums(obj: dict, enums: dict, errors: dict) -> None:
    for key, allowed in enums.items():
        value = obj.get(key)
        if value not in (None, "") and value not in allowed:
            raise ValueError(errors["enum_out"].format(key=key, value=value, allowed=sorted(allowed)))


def _check_voice(voice: dict, errors: dict) -> None:
    _check_enums(voice, VOICE_ENUMS, errors)
    for req in ("age", "pitch", "texture", "breathiness"):
        if req not in voice:
            raise ValueError(errors["missing_voice_field"].format(field=req))


def _check_characters(data: dict, errors: dict) -> None:
    chars = data.get("characters")
    if not isinstance(chars, list):
        raise ValueError(errors["not_a_list"].format(key="characters"))
    for c in chars:
        if not isinstance(c, dict) or not c.get("name"):
            raise ValueError(errors["missing_name_char"])
        _check_voice(c.get("voice") or {}, errors)


def _check_character(data: dict, errors: dict) -> None:
    _check_voice(data.get("voice") or {}, errors)


def _check_perf_fields(p: dict, errors: dict) -> None:
    if not p.get("emotion"):
        raise ValueError(errors["missing_emotion"])
    _check_enums(p, PERF_ENUMS, errors)


def _check_performances(data: dict, errors: dict) -> None:
    perfs = data.get("performances")
    if not isinstance(perfs, list):
        raise ValueError(errors["not_a_list"].format(key="performances"))
    for p in perfs:
        if not isinstance(p, dict) or not p.get("name"):
            raise ValueError(errors["missing_name_perf"])
        _check_perf_fields(p, errors)


def _check_performance(data: dict, errors: dict) -> None:
    _check_perf_fields(data, errors)


def _distill(system: str, user: str, expect_key: str | None = None, check=None, attempts: int = 3,
             lang: str | None = None) -> dict:
    """LLM を呼んで JSON を得る。構造・enum が崩れたら再生成する（手で直さない）。"""
    from semantic_audio_loom.llm.client import ClaudeClient

    prompts = i18n.load_prompts(lang)
    errors = prompts["distill"]["errors"]
    retry_tmpl = prompts["distill"]["retry"]
    client = ClaudeClient()
    prompt = user
    for attempt in range(attempts):
        try:
            data = client.complete_json(system, prompt)
            if expect_key is not None and expect_key not in data:
                raise ValueError(errors["missing_key"].format(key=expect_key))
            if check is not None:
                check(data, errors)
            return data
        except Exception as exc:
            if attempt == attempts - 1:
                raise
            prompt = user + "\n\n" + retry_tmpl.format(exc=exc)


def distill_characters(text: str, lang: str | None = None) -> list[dict]:
    system = i18n.load_prompts(lang)["distill"]["characters"]
    data = _distill(system, text, expect_key="characters", check=_check_characters, lang=lang)
    return data.get("characters", [])


def distill_performances(text: str, lang: str | None = None) -> list[dict]:
    system = i18n.load_prompts(lang)["distill"]["performances"]
    data = _distill(system, text, expect_key="performances", check=_check_performances, lang=lang)
    return data.get("performances", [])


def distill_character(text: str, lang: str | None = None) -> dict:
    system = i18n.load_prompts(lang)["distill"]["character"]
    return _distill(system, text, check=_check_character, lang=lang)


def distill_performance(text: str, lang: str | None = None) -> dict:
    system = i18n.load_prompts(lang)["distill"]["performance"]
    return _distill(system, text, check=_check_performance, lang=lang)


def slug(name: str) -> str:
    """資材名（ファイル名の接頭辞）を正規化する：小文字・非英数字→ハイフン。"""
    s = (name or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return s or "unnamed"


def write_character(asset: dict, overwrite: bool = False, lang: str | None = None) -> str:
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
        raise FileExistsError(
            i18n._t(i18n.load_locale(lang), "distill", "exists",
                    "{path} は既にあります（--overwrite で上書き）", path=path)
        )
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(profile, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
    return path


def write_performance(asset: dict, overwrite: bool = False, lang: str | None = None) -> str:
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
        raise FileExistsError(
            i18n._t(i18n.load_locale(lang), "distill", "exists",
                    "{path} は既にあります（--overwrite で上書き）", path=path)
        )
    with open(path, "w", encoding="utf-8") as f:
        yaml.safe_dump(direction, f, allow_unicode=True, sort_keys=False, default_flow_style=False)
    return path
