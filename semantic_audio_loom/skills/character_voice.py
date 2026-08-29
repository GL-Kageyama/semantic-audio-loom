"""character-voice Skill（キャラの再利用を担う糊）。

.voice.yaml（voice_profile.schema.json 準拠）を読み、台詞と Direction から
GenerationIntent を組み立てる。

キャラ資材（.voice.yaml）は「キャラ作り」の産物で、`characters/` に置いて
名前で再利用する。声の生成（bin/generate.py）はここから名前解決して参照する。
"""
from __future__ import annotations

import os

from semantic_audio_loom import config
from semantic_audio_loom.text import annotate_reading, parse_ruby
from semantic_audio_loom.types import GenerationIntent


def load_voice_profile(path: str) -> dict:
    import yaml

    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def character_path(name: str) -> str:
    """キャラ名 → characters/<name>.voice.yaml のパス（拡張子は補完可）。"""
    if name.endswith((".yaml", ".yml")):
        name = name.rsplit(".", 1)[0]
    path = os.path.join(config.CHARACTERS_DIR, name + ".voice.yaml")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"キャラクター '{name}' が見つかりません: {path}（bin/character.py init {name} で作成）"
        )
    return path


def list_characters() -> list[str]:
    """characters/ にあるキャラ名（.voice.yaml の接頭辞）を返す。"""
    if not os.path.isdir(config.CHARACTERS_DIR):
        return []
    names = []
    for fname in sorted(os.listdir(config.CHARACTERS_DIR)):
        if fname.endswith(".voice.yaml"):
            names.append(fname[: -len(".voice.yaml")])
    return names


def name_reading_registry() -> dict[str, str]:
    """キャラ表示名 → 読み の一覧（`name_reading` を持つキャラのみ）。

    台詞中のキャラ名（固有名詞）に自動でルビを振るために使う。phonemize が
    固有名詞を誤読する（例: 「真白」→「まっしろ」）ため、`characters/` の
    `name_reading` から読みを引き当てる。
    """
    registry: dict[str, str] = {}
    for name in list_characters():
        try:
            vp = load_voice_profile(character_path(name))
        except (OSError, FileNotFoundError):
            continue
        display = vp.get("character")
        reading = vp.get("name_reading")
        if display and reading:
            registry[display] = reading
    return registry


def build_intent(
    voice_profile: dict,
    dialogue: str,
    emotion: str = "neutral",
    intensity: str = "none",
    performance: dict | None = None,
    situation: str = "",
    state: dict | None = None,
    subtext: str = "",
    seed: int | None = None,
) -> GenerationIntent:
    # キャラ名（固有名詞）の読みを、voice.yaml の name_reading から自動でルビ化する。
    # 現在のキャラ（--character-file 等で characters/ 外の可能性）も加味する。
    registry = name_reading_registry()
    display = voice_profile.get("character")
    name_reading = voice_profile.get("name_reading")
    if display and name_reading:
        registry[display] = name_reading
    for word, reading in registry.items():
        dialogue = annotate_reading(dialogue, word, reading)

    # 台詞にふりがな《》があれば、表示用台詞（dialogue）と読み（reading）に分離する。
    clean, reading = parse_ruby(dialogue)
    return GenerationIntent(
        asset_type="voice",
        voice_profile=voice_profile,
        situation=situation,
        character_state=state or {},
        emotion={"primary": emotion, "intensity": intensity},
        performance=performance or {},
        subtext=subtext,
        dialogue=clean,
        reading=reading,
        seed=seed,
    )
