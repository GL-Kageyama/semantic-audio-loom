"""ふりがな《》記法（読みの指定）のテスト。

Tsukasa の phonemize（cutlet）が「既読」→ kijomi と誤読する問題への対処として、
`parse_ruby` が台詞を（表示用台詞, 読み）に正しく分解することを検証する。
"""
from __future__ import annotations

from semantic_audio_loom.text import annotate_reading, parse_ruby


def test_single_ruby_splits_dialogue_and_reading():
    line = "既読《きどく》を付けて、画面を閉じる。"
    dialogue, reading = parse_ruby(line)
    assert dialogue == "既読を付けて、画面を閉じる。"
    assert reading == "きどくを付けて、画面を閉じる。"


def test_multiple_ruby_substitutes_and_strips_all():
    line = "既読《きどく》と、午前二時《ごぜんにじ》。"
    dialogue, reading = parse_ruby(line)
    assert dialogue == "既読と、午前二時。"
    assert reading == "きどくと、ごぜんにじ。"


def test_no_ruby_returns_text_and_empty_reading():
    line = "おはよう。"
    dialogue, reading = parse_ruby(line)
    assert dialogue == "おはよう。"
    assert reading == ""


def test_unbalanced_ruby_is_untouched():
    line = "既読《きどくを付けて"
    dialogue, reading = parse_ruby(line)
    assert dialogue == line
    assert reading == ""


def test_annotate_reading_wraps_word():
    assert annotate_reading("真白は、布団の中で。", "真白", "ましろ") == \
        "真白《ましろ》は、布団の中で。"


def test_annotate_reading_skips_already_annotated():
    line = "真白《ましろ》は、既読《きどく》を付ける。"
    assert annotate_reading(line, "真白", "ましろ") == line


def test_annotate_reading_noop_when_word_absent():
    assert annotate_reading("こんにちは。", "真白", "ましろ") == "こんにちは。"
