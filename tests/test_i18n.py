"""i18n（en/ja/zh）のテスト：言語解決・キー整合・プロンプト言語・CLI --lang スモーク。

LLM はモック（complete_json を差し替え）。実 API は呼ばない。
"""
import os
import subprocess
import sys

import pytest

from semantic_audio_loom import i18n
from semantic_audio_loom.engine import distill, resolve as resolve_mod
from semantic_audio_loom.llm.client import ClaudeClient
from semantic_audio_loom.types import GenerationIntent

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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


def _has_japanese_kana(s: str) -> bool:
    for c in s:
        o = ord(c)
        if 0x3040 <= o <= 0x309F:  # ひらがな
            return True
        if 0x30A0 <= o <= 0x30FF and c != "・":  # カタカナ（中点は共用句読点として除外）
            return True
    return False


def _walk(obj, prefix=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield from _walk(v, f"{prefix}.{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from _walk(v, f"{prefix}[{i}]")
    else:
        yield prefix, obj


# ---- 言語解決 ----

def test_resolve_lang_default_is_ja(monkeypatch):
    monkeypatch.delenv("SAL_LANG", raising=False)
    assert i18n.resolve_lang(None) == "ja"


def test_resolve_lang_env(monkeypatch):
    monkeypatch.setenv("SAL_LANG", "zh")
    assert i18n.resolve_lang(None) == "zh"


def test_resolve_lang_cli_overrides_env(monkeypatch):
    monkeypatch.setenv("SAL_LANG", "zh")
    assert i18n.resolve_lang("en") == "en"


def test_resolve_lang_unsupported_falls_back(monkeypatch, capsys):
    monkeypatch.setenv("SAL_LANG", "fr")
    assert i18n.resolve_lang(None) == "ja"
    assert "fr" in capsys.readouterr().err


# ---- キー整合 ----

def test_locale_keys_consistent():
    ja = i18n.load_locale("ja")
    for lang in ("en", "zh"):
        loc = i18n.load_locale(lang)
        for section, keys in ja.items():
            if section == "_meta":
                continue
            assert section in loc, (lang, section)
            for k in keys:
                assert k in loc[section], (lang, section, k)


def test_prompt_keys_consistent():
    ja = i18n.load_prompts("ja")
    for lang in ("en", "zh"):
        pr = i18n.load_prompts(lang)
        assert set(pr) == set(ja)
        assert set(pr["resolve"]) == set(ja["resolve"])
        assert set(pr["distill"]) == set(ja["distill"])
        assert set(pr["distill"]["errors"]) == set(ja["distill"]["errors"])


# ---- 日本語（かな）漏れ ----

@pytest.mark.parametrize("lang", ["en", "zh"])
def test_prompts_have_no_japanese_kana(lang):
    pr = i18n.load_prompts(lang)
    for key, val in _walk(pr):
        if isinstance(val, str) and _has_japanese_kana(val):
            raise AssertionError(f"kana leaked into prompts.{lang}{key}: {val[:80]!r}")


def test_ja_prompts_are_japanese():
    # 正本（ja）は日本語プロンプトであることの健全性確認。
    system = i18n.load_prompts("ja")["resolve"]["system"]
    assert _has_japanese_kana(system)


# ---- プロンプト言語（モック LLM 完走） ----

def test_distill_prompt_localized_by_lang(monkeypatch):
    captured = {}

    def fake(self, system, user):
        captured["system"] = system
        return {"characters": [GOOD_CHARACTER]}

    monkeypatch.setattr(ClaudeClient, "complete_json", fake)

    distill.distill_characters("a story", lang="en")
    assert "vocal essence" in captured["system"]
    assert not _has_japanese_kana(captured["system"])

    distill.distill_characters("物語", lang="zh")
    assert "蒸馏" in captured["system"]
    assert not _has_japanese_kana(captured["system"])

    distill.distill_characters("物語", lang="ja")
    assert _has_japanese_kana(captured["system"])


def test_resolve_prompt_localized_by_lang(monkeypatch):
    captured = {}

    def fake(self, system, user):
        captured["system"] = system
        captured["user"] = user
        return {"emotion": {"primary": "anxiety", "intensity": 0.5},
                "subtext": "afraid of the reply"}

    monkeypatch.setattr(ClaudeClient, "complete_json", fake)

    intent = GenerationIntent(dialogue="……まだ、起きてる？", situation="深夜の電話",
                              emotion={"primary": "anxiety"}, subtext="返事が怖い")
    spec = resolve_mod.resolve_llm(intent, lang="en")
    assert spec["subtext"] == "afraid of the reply"
    # 台詞は日本語のまま（領域事実）。ラベルは英語。
    assert "Line:" in captured["user"]
    assert "Situation:" in captured["user"]
    assert "……まだ、起きてる？" in captured["user"]
    assert not _has_japanese_kana(captured["system"])


def test_distill_enum_stays_english(monkeypatch):
    # enum 外の日本語ピッチ → 再生成（enum は英語固定）を確認。
    bad_voice = dict(GOOD_CHARACTER["voice"], pitch="超高音")
    bad = {"characters": [dict(GOOD_CHARACTER, voice=bad_voice)]}
    idx = {"i": 0}
    responses = [bad, {"characters": [GOOD_CHARACTER]}]

    def fake(self, system, user):
        r = responses[min(idx["i"], len(responses) - 1)]
        idx["i"] += 1
        return r

    monkeypatch.setattr(ClaudeClient, "complete_json", fake)
    chars = distill.distill_characters("a story", lang="en")
    assert chars[0]["voice"]["pitch"] == "medium_high"


# ---- CLI --lang スモーク ----

def _run_cli(*argv):
    env = dict(os.environ)
    env.pop("SAL_LANG", None)  # 既定 ja を素のプロセスで確認するため env を外す
    return subprocess.run(
        [sys.executable, os.path.join(REPO, "bin", "character.py"), *argv],
        capture_output=True, text=True, env=env,
    )


def test_cli_lang_en_help():
    r = _run_cli("--lang", "en", "--help")
    assert r.returncode == 0
    assert "List registered characters" in r.stdout
    assert "登録済みキャラ一覧" not in r.stdout


def test_cli_default_ja_help():
    r = _run_cli("--help")
    assert r.returncode == 0
    assert "登録済みキャラ一覧" in r.stdout
