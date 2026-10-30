"""sound Skill（非 voice の Direction を GenerationIntent へ組み立てる糊）。

bgm / ambience / sfx / foley は「Sound Direction」を書く。声の Performance Direction
（emotion・volume・delivery）に対応する層で、意味フィールドは type ごとに違う：

- bgm       … role / genre / mood / tempo / key / instrumentation / arrangement / texture
- ambience  … environment / location / time / weather / space / density / movement
- sfx       … event / object / material / distance / intensity
- foley     … action / object / surface / contact

Sound Bible（projects/<project>/sound-bible.yaml）は作品全体の音響スタイルで、
Direction の未指定フィールド（style / palette / negative）を供給する。
"""
from __future__ import annotations

import os

from semantic_audio_loom import config
from semantic_audio_loom.types import GenerationIntent

# asset_type → Sound Bible のセクション名
BIBLE_SECTIONS = {
    "bgm": "music",
    "ambience": "ambience",
    "sfx": "sfx",
    "foley": "foley",
}

# Sound Bible が Direction へ供給するキー（Direction が優先）。
_BIBLE_KEYS = ("style", "instrumentation", "palette")

# 配列として書くキー。CLI の `key=value` で 1 語だけ渡されたとき、この集合なら
# [value] に包む（`--sound instrumentation=solo_piano` を通すため）。
LIST_KEYS = frozenset(
    {"genre", "mood", "style", "instrumentation", "texture", "references", "negative", "tags"}
)


def build_intent(
    asset_type: str,
    sound: dict | None = None,
    situation: str = "",
    scene: dict | None = None,
    subtext: str = "",
    seed: int | None = None,
) -> GenerationIntent:
    if asset_type == "voice":
        raise ValueError("voice は skills/character_voice.build_intent を使う")
    return GenerationIntent(
        asset_type=asset_type,
        sound=dict(sound or {}),
        situation=situation,
        scene=scene or {},
        subtext=subtext,
        seed=seed,
    )


def bible_path(project: str) -> str:
    return os.path.join(config.project_dir(project), "sound-bible.yaml")


def load_bible(path: str) -> dict:
    import yaml

    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def apply_bible(asset_type: str, bible: dict, sound: dict) -> dict:
    """Sound Bible のスタイルを Direction へ足す（Direction の明示指定は上書きしない）。"""
    section = (bible or {}).get(BIBLE_SECTIONS.get(asset_type, ""), {}) or {}
    merged = dict(sound or {})
    for key in _BIBLE_KEYS:
        value = section.get(key)
        if value and not merged.get(key):
            merged[key] = value
    negative = section.get("negative")
    if negative:
        merged["negative"] = list(merged.get("negative") or []) + list(negative)
    return merged
