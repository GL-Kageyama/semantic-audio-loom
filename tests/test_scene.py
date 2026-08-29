"""Scene（場面＝複数キュー）の読み込み・検証・再構成のテスト。"""
from __future__ import annotations

import os
import tempfile

import pytest

from semantic_audio_loom.engine.validate import validate_scene
from semantic_audio_loom.scene import cue_from_params, load_scene
from semantic_audio_loom.types import Scene, SceneCue


def _load(content: str) -> Scene:
    with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False, encoding="utf-8") as f:
        f.write(content)
        path = f.name
    try:
        return load_scene(path)
    finally:
        os.remove(path)


def test_load_scene_folds_flat_direction_into_performance():
    scene = _load(
        """\
name: demo
default_pause: 0.5
cues:
  - character: 真白
    line: おはよう。
    emotion: joy
    volume: quiet
    speed: slow
    delivery: gentle
    pause_before: 0.8
  - character: ニジ
    line: 起きてる？
"""
    )
    assert scene.name == "demo"
    assert scene.default_pause == 0.5
    assert len(scene.cues) == 2

    c0 = scene.cues[0]
    assert c0.character == "真白"
    assert c0.emotion == "joy"
    assert c0.performance == {"volume": "quiet", "speed": "slow", "delivery": "gentle"}
    assert c0.pause_before == 0.8

    c1 = scene.cues[1]
    assert c1.pause_before is None  # 未指定 → default_pause を継承
    assert c1.performance == {}


def test_validate_scene_ok():
    validate_scene(Scene(name="s", cues=[SceneCue(character="真白", line="おはよう。")]))


def test_validate_scene_missing_character_raises():
    with pytest.raises(Exception):
        validate_scene(Scene(cues=[SceneCue(character="", line="おはよう。")]))


def test_validate_scene_missing_line_raises():
    with pytest.raises(Exception):
        validate_scene(Scene(cues=[SceneCue(character="真白", line="")]))


def test_validate_scene_negative_pause_raises():
    with pytest.raises(Exception):
        validate_scene(Scene(cues=[SceneCue(character="真白", line="x", pause_before=-1.0)]))


def test_validate_scene_unknown_emotion_raises():
    with pytest.raises(Exception):
        validate_scene(Scene(cues=[SceneCue(character="真白", line="x", emotion="bogus")]))


def test_cue_from_params_reconstructs_request():
    cue = {
        "voice_profile": {"character": "真白", "voice": {}},
        "performance_spec": {"emotion": {"primary": "calm", "intensity": 0.25}},
        "dialogue": "おはよう。",
        "reading": "",
        "seed": 42,
        "provider": "tsukasa",
    }
    req = cue_from_params(cue)
    assert req.asset_type == "voice"
    assert req.seed == 42
    assert req.dialogue == "おはよう。"
    assert req.reading == ""
    assert req.provider_hint == "tsukasa"
    assert req.voice_profile["character"] == "真白"
