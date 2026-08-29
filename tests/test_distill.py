"""engine/distill.py と bin/distill.py の蒸留機構のテスト。

LLM はモック（ClaudeClient.complete_json を差し替え）。実 API は呼ばない。
"""
import os

import pytest

from semantic_audio_loom import config
from semantic_audio_loom.engine import distill
from semantic_audio_loom.llm.client import ClaudeClient

GOOD_CHARACTER = {
    "name": "mashiro",
    "character": "真白",
    "voice": {
        "age": "young_adult",
        "gender": "female",
        "pitch": "medium_high",
        "texture": "soft",
        "breathiness": "slight",
        "resonance": "head",
    },
}
GOOD_PERFORMANCE = {
    "name": "anxious-night-call",
    "emotion": "anxiety",
    "intensity": "moderate",
    "volume": "quiet",
    "speed": "slow",
    "pitch": "slightly_low",
    "breathiness": "slight",
    "delivery": "hesitant",
    "situation": "深夜の電話",
    "subtext": "返事が怖いが、繋がりを求めてしまう。",
}


@pytest.fixture(autouse=True)
def _fake_auth(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")


def _respond(monkeypatch, *responses):
    """complete_json が responses を順に返すよう差し替える（枯渇時は最後のを繰り返す）。"""
    idx = {"i": 0}

    def fake(self, system, user):
        r = responses[min(idx["i"], len(responses) - 1)]
        idx["i"] += 1
        return r

    monkeypatch.setattr(ClaudeClient, "complete_json", fake)


def test_slug():
    assert distill.slug("Mashiro") == "mashiro"
    assert distill.slug("Anxious Night Call!") == "anxious-night-call"
    assert distill.slug("  Rei  ") == "rei"
    assert distill.slug("真白") == "unnamed"


def test_distill_characters(monkeypatch):
    _respond(monkeypatch, {"characters": [GOOD_CHARACTER]})
    chars = distill.distill_characters("ある物語")
    assert len(chars) == 1
    assert chars[0]["name"] == "mashiro"


def test_distill_characters_enum_out_then_fixed(monkeypatch):
    bad_voice = dict(GOOD_CHARACTER["voice"], pitch="超高音")
    bad = {"characters": [dict(GOOD_CHARACTER, voice=bad_voice)]}
    _respond(monkeypatch, bad, {"characters": [GOOD_CHARACTER]})
    chars = distill.distill_characters("ある物語")
    assert chars[0]["voice"]["pitch"] == "medium_high"


def test_distill_character(monkeypatch):
    _respond(monkeypatch, {"character": "真白", "voice": GOOD_CHARACTER["voice"]})
    data = distill.distill_character("金髪の少女")
    assert data["character"] == "真白"


def test_distill_performances(monkeypatch):
    _respond(monkeypatch, {"performances": [GOOD_PERFORMANCE]})
    perfs = distill.distill_performances("ある物語")
    assert len(perfs) == 1
    assert perfs[0]["emotion"] == "anxiety"


def test_write_character(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "CHARACTERS_DIR", str(tmp_path))
    path = distill.write_character(dict(GOOD_CHARACTER))
    assert os.path.exists(path)
    from semantic_audio_loom.skills.character_voice import load_voice_profile

    prof = load_voice_profile(path)
    assert prof["character"] == "真白"
    assert prof["voice"]["pitch"] == "medium_high"


def test_write_character_refuses_overwrite(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "CHARACTERS_DIR", str(tmp_path))
    distill.write_character(dict(GOOD_CHARACTER))
    with pytest.raises(FileExistsError):
        distill.write_character(dict(GOOD_CHARACTER))
    # overwrite=True なら上書きできる
    distill.write_character(dict(GOOD_CHARACTER), overwrite=True)


def test_write_character_invalid_missing_field(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "CHARACTERS_DIR", str(tmp_path))
    bad = dict(GOOD_CHARACTER)
    bad["voice"] = dict(GOOD_CHARACTER["voice"])
    del bad["voice"]["texture"]
    with pytest.raises(Exception):
        distill.write_character(bad)


def test_write_performance(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "PERFORMANCES_DIR", str(tmp_path))
    path = distill.write_performance(dict(GOOD_PERFORMANCE))
    assert os.path.exists(path)
    from semantic_audio_loom.skills.performance import load_direction

    d = load_direction(path)
    assert d["emotion"] == "anxiety"


def test_write_performance_requires_emotion(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "PERFORMANCES_DIR", str(tmp_path))
    bad = dict(GOOD_PERFORMANCE)
    bad.pop("emotion")
    with pytest.raises(Exception):
        distill.write_performance(bad)
