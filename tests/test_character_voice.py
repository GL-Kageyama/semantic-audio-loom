"""build_intent のキャラ名（固有名詞）自動ルビのテスト。

phonemize が「真白」を「まっしろ」と誤読する問題への対処として、voice.yaml の
`name_reading` から台詞中のキャラ名へ自動でルビを振ることを検証する。
"""
from __future__ import annotations

from semantic_audio_loom.skills import character_voice
from semantic_audio_loom.skills.character_voice import build_intent


def _vp(character="語り", name_reading=None):
    vp = {"character": character, "voice": {"age": "adult", "gender": "female",
          "pitch": "medium", "texture": "neutral", "breathiness": "slight", "resonance": "chest"}}
    if name_reading:
        vp["name_reading"] = name_reading
    return vp


def test_build_intent_auto_annotates_character_name(monkeypatch):
    monkeypatch.setattr(character_voice, "name_reading_registry", lambda: {"真白": "ましろ"})
    intent = build_intent(_vp(), "真白は、布団の中で。", seed=1)
    assert intent.dialogue == "真白は、布団の中で。"
    assert intent.reading == "ましろは、布団の中で。"


def test_build_intent_manual_ruby_coexists_with_auto_annotation(monkeypatch):
    monkeypatch.setattr(character_voice, "name_reading_registry", lambda: {"真白": "ましろ"})
    # 手書きルビ（既読）と自動ルビ（真白）が共存し、両方とも読みへ反映される
    line = "既読《きどく》を付けて、真白は、画面を閉じた。"
    intent = build_intent(_vp(), line, seed=1)
    assert intent.dialogue == "既読を付けて、真白は、画面を閉じた。"
    assert intent.reading == "きどくを付けて、ましろは、画面を閉じた。"


def test_build_intent_no_reading_when_registry_empty(monkeypatch):
    monkeypatch.setattr(character_voice, "name_reading_registry", lambda: {})
    intent = build_intent(_vp(), "真白は、布団の中で。", seed=1)
    assert intent.dialogue == "真白は、布団の中で。"
    assert intent.reading == ""
