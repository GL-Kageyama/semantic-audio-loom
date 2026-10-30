"""非 voice（bgm / ambience / sfx / foley）の生成経路とライブラリのテスト。

重いモデルは使わず、stub Provider で 7 段フロー（Validate → Route → Resolve →
Generate → Normalize → Tag → Store）が全 type で通ることを確かめる。
"""
from __future__ import annotations

import os
import subprocess
import sys
import wave

import numpy as np
import pytest
import yaml

from semantic_audio_loom import config
from semantic_audio_loom.engine import AudioAssetEngine, normalize, resolve, route, validate
from semantic_audio_loom.skills import library, sound
from semantic_audio_loom.types import Audio, GenerationIntent

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_VOICE_PROFILE = {
    "character": "真白",
    "voice": {"age": "young_adult", "pitch": "medium", "texture": "soft", "breathiness": "slight"},
}


# ---------------------------------------------------------------- Resolve


def test_music_rule_spec_is_valid_and_prompt_is_concrete():
    intent = sound.build_intent(
        "bgm",
        {
            "role": "underscore",
            "mood": ["lonely"],
            "instrumentation": ["solo piano"],
            "tempo": {"bpm": 60},
            "duration": 20,
        },
    )
    spec = resolve.resolve(intent, mode="rule")
    validate.validate_spec(spec, "bgm")
    assert "solo piano" in spec["prompt"]
    assert "no vocals" in spec["prompt"]
    assert spec["duration"] == 20


def test_music_rule_keeps_explicit_prompt():
    intent = sound.build_intent("bgm", {"prompt": "warm tape loop, no drums"})
    spec = resolve.resolve(intent, mode="rule")
    assert spec["prompt"] == "warm tape loop, no drums"


@pytest.mark.parametrize(
    "kind,fields,required_key",
    [
        ("ambience", {"environment": "empty train station", "time": "night"}, "environment"),
        ("sfx", {"event": "heavy wooden door closing"}, "event"),
        ("sfx", {"object": "glass bottle"}, "object"),
        ("foley", {"action": "footsteps on gravel"}, "action"),
    ],
)
def test_sound_rule_spec_is_valid(kind, fields, required_key):
    intent = sound.build_intent(kind, fields)
    spec = resolve.resolve(intent, mode="rule")
    validate.validate_spec(spec, kind)
    assert spec["kind"] == kind
    assert spec[required_key]


def test_sound_rule_falls_back_to_situation():
    intent = sound.build_intent("sfx", situation="a sword striking a shield")
    spec = resolve.resolve(intent, mode="rule")
    validate.validate_spec(spec, "sfx")
    assert spec["event"] == "a sword striking a shield"


def test_sound_intent_rejects_unknown_enum_early():
    with pytest.raises(Exception):
        validate.validate_intent(
            GenerationIntent(asset_type="ambience", sound={"space": "underwater"})
        )


# ---------------------------------------------------------------- 7 段フロー


def _read_wav(path):
    with wave.open(path, "rb") as w:
        frames = w.readframes(w.getnframes())
    return {
        "channels": w.getnchannels(),
        "sample_rate": w.getframerate(),
        "samples": np.frombuffer(frames, dtype=np.int16),
    }


@pytest.mark.parametrize("asset_type", ["bgm", "ambience", "sfx", "foley"])
def test_stub_engine_round_trip(tmp_path, asset_type):
    sound_direction = {
        "bgm": {"mood": ["calm"], "duration": 1.0},
        "ambience": {"environment": "quiet room", "duration": 1.0},
        "sfx": {"event": "single click", "duration": 0.5},
        "foley": {"action": "cloth rustle", "duration": 0.5},
    }[asset_type]
    engine = AudioAssetEngine(provider_name="stub", resolve_mode="rule")
    asset = engine.generate(
        sound.build_intent(asset_type, sound_direction), out_dir=str(tmp_path), name=asset_type
    )

    assert asset.path == os.path.join(str(tmp_path), asset_type + ".wav")
    assert asset.parameters["asset_type"] == asset_type
    assert asset.parameters["version"] == 3
    validate.validate_spec(asset.parameters["spec"], asset_type)

    info = _read_wav(asset.path)
    assert info["sample_rate"] == 44100
    assert asset.metadata["sample_rate"] == 44100
    assert asset.metadata["channels"] == info["channels"]
    assert asset.metadata["duration"] > 0
    if asset_type in ("bgm", "ambience"):
        assert info["channels"] == 2  # 生成のステレオを潰さない
    else:
        assert info["channels"] == 1

    with open(os.path.join(str(tmp_path), asset_type + ".params.yaml"), encoding="utf-8") as f:
        saved = yaml.safe_load(f)
    assert saved["parameters"]["spec"]["prompt"]


def test_voice_path_still_works_with_new_request(tmp_path):
    engine = AudioAssetEngine(provider_name="stub", resolve_mode="rule")
    intent = GenerationIntent(
        asset_type="voice",
        voice_profile=_VOICE_PROFILE,
        emotion={"primary": "joy", "intensity": "moderate"},
        dialogue="おはよう。",
        seed=7,
    )
    asset = engine.generate(intent, out_dir=str(tmp_path), name="voice")
    assert asset.parameters["version"] == 2
    assert asset.parameters["performance_spec"]["emotion"]["primary"] == "joy"
    assert _read_wav(asset.path)["channels"] == 1
    assert _read_wav(asset.path)["sample_rate"] == config.SAMPLE_RATE


# ---------------------------------------------------------------- Normalize


def test_normalize_resamples_and_keeps_stereo():
    sr = 32000
    t = np.arange(sr, dtype=np.float32) / sr
    wav = np.stack([np.sin(2 * np.pi * 220 * t), np.sin(2 * np.pi * 330 * t)], axis=1)
    out = normalize.normalize(Audio(wav=wav, sample_rate=sr), sample_rate=44100, tail_fade_ms=None)
    assert out.sample_rate == 44100
    assert out.wav.shape[1] == 2
    assert abs(out.wav.shape[0] - 44100) <= 2
    assert float(np.max(np.abs(out.wav))) <= 0.951


def test_normalize_downmixes_to_mono_when_asked():
    wav = np.ones((1000, 2), dtype=np.float32) * 0.1
    out = normalize.normalize(Audio(wav=wav, sample_rate=44100), channels=1, tail_fade_ms=None)
    assert out.wav.ndim == 1
    assert out.wav.shape[0] == 1000


def test_normalize_accepts_channels_first_provider_output():
    # diffusers は (channels, samples) を返す。
    wav = np.zeros((2, 4410), dtype=np.float32)
    wav[0] = 0.5
    out = normalize.normalize(Audio(wav=wav, sample_rate=44100), tail_fade_ms=None)
    assert out.wav.shape == (4410, 2)


# ---------------------------------------------------------------- Route


def test_route_rejects_provider_without_capability():
    with pytest.raises(ValueError, match="cannot generate"):
        route.route("bgm", "tsukasa")


def test_route_defaults_are_registered():
    for asset_type, name in route.DEFAULTS.items():
        assert name in __import__("semantic_audio_loom.providers", fromlist=["available"]).available()


# ---------------------------------------------------------------- Sound Bible


def test_apply_bible_fills_only_missing_fields():
    bible = {
        "music": {
            "style": ["lofi"],
            "instrumentation": ["piano"],
            "negative": ["drums"],
        }
    }
    merged = sound.apply_bible("bgm", bible, {"instrumentation": ["cello"]})
    assert merged["style"] == ["lofi"]
    assert merged["instrumentation"] == ["cello"]  # Direction が優先
    assert merged["negative"] == ["drums"]


def test_sound_bible_template_validates(tmp_path, monkeypatch):
    path = tmp_path / "sound-bible.yaml"
    path.write_text(
        "project: demo\nmusic:\n  style: [lofi]\nsfx:\n  palette: [wood]\n", encoding="utf-8"
    )
    doc = sound.load_bible(str(path))
    validate.validate_sound_bible(doc)


# ---------------------------------------------------------------- Library


@pytest.fixture()
def library_dir(tmp_path, monkeypatch):
    target = tmp_path / "library"
    monkeypatch.setattr(config, "LIBRARY_DIR", str(target))
    return target


def test_library_add_and_search(library_dir):
    engine = AudioAssetEngine(provider_name="stub", resolve_mode="rule")
    asset = engine.generate(
        sound.build_intent("sfx", {"event": "heavy wooden door closing", "duration": 0.5}),
        out_dir=str(library_dir),
        name="door-close",
    )
    doc = library.add_generated(
        asset, "sfx", "door-close", tags=["door", "wood"], license="generated"
    )

    assert (library_dir / "sfx" / "door-close.wav").exists()
    assert (library_dir / "sfx" / "door-close.asset.yaml").exists()
    assert doc["duration"] > 0
    assert doc["semantic"]["event"] == "heavy wooden door closing"
    assert doc["source"]["provider"] == "stub"

    assert [d["name"] for d in library.search("door")] == ["door-close"]
    assert [d["name"] for d in library.search("wood", tags=["door"])] == ["door-close"]
    assert library.search("piano") == []
    assert library.find("door-close", "sfx")["name"] == "door-close"
    assert library.validate_all() == []


def test_library_add_wav_records_info(library_dir):
    src = library_dir / "src.wav"
    src.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(src), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(44100)
        w.writeframes(np.zeros(44100, dtype=np.int16).tobytes())

    doc = library.add_wav(str(src), "ambience", "room-tone", tags=["room"])
    assert doc["sample_rate"] == 44100
    assert doc["channels"] == 1
    assert abs(doc["duration"] - 1.0) < 0.01
    assert library.validate_all() == []


def test_library_validate_reports_missing_wav(library_dir):
    folder = library_dir / "sfx"
    folder.mkdir(parents=True)
    (folder / "ghost.asset.yaml").write_text(
        yaml.safe_dump(
            {"name": "ghost", "asset_type": "sfx", "files": {"wav": "ghost.wav"}},
            allow_unicode=True,
        ),
        encoding="utf-8",
    )
    problems = library.validate_all()
    assert len(problems) == 1 and "missing wav" in problems[0]


# ---------------------------------------------------------------- Provider


def test_provider_registry_lists_all():
    from semantic_audio_loom import providers

    assert providers.available() == ["musicgen", "stable_audio", "stub", "tsukasa"]


def test_stable_audio_without_diffusers_names_the_install():
    import importlib.util

    from semantic_audio_loom.providers.stable_audio import StableAudioProvider
    from semantic_audio_loom.types import GenerationRequest

    if importlib.util.find_spec("diffusers") is not None:
        pytest.skip("diffusers is installed")
    with pytest.raises(RuntimeError, match="diffusers"):
        StableAudioProvider().generate(
            GenerationRequest(asset_type="sfx", spec={"prompt": "door slam"}, seed=1)
        )


# ---------------------------------------------------------------- 空の検査


def _run_cli(script: str, *argv: str, env_extra: dict | None = None):
    env = dict(os.environ)
    env.pop("SAL_LANG", None)  # 既定 ja の文言を確かめるため
    env.update(env_extra or {})
    return subprocess.run(
        [sys.executable, os.path.join(REPO, "bin", script), *argv],
        capture_output=True, text=True, env=env,
    )


def test_library_validate_empty_is_not_called_healthy(tmp_path):
    # 0 件を「健全」と言わない（何も検査していない）。
    r = _run_cli("library.py", "validate", env_extra={"SAL_LIBRARY_DIR": str(tmp_path / "none")})
    assert r.returncode == 0
    assert "健全" not in r.stdout
    assert "ありません" in r.stdout


def test_sound_bible_validate_empty_sections_is_not_called_healthy(tmp_path):
    r = _run_cli("sound-bible.py", "init", "demo",
                 env_extra={"SAL_PROJECTS_DIR": str(tmp_path)})
    assert r.returncode == 0, r.stderr
    r = _run_cli("sound-bible.py", "validate", "demo",
                 env_extra={"SAL_PROJECTS_DIR": str(tmp_path)})
    assert r.returncode == 0, r.stderr
    assert "健全" not in r.stdout
    assert "空です" in r.stdout


def test_sound_bible_validate_filled_is_healthy(tmp_path):
    r = _run_cli("sound-bible.py", "init", "demo",
                 env_extra={"SAL_PROJECTS_DIR": str(tmp_path)})
    assert r.returncode == 0, r.stderr
    path = tmp_path / "demo" / "sound-bible.yaml"
    path.write_text("project: demo\nmusic:\n  style: [lofi]\n", encoding="utf-8")
    r = _run_cli("sound-bible.py", "validate", "demo",
                 env_extra={"SAL_PROJECTS_DIR": str(tmp_path)})
    assert r.returncode == 0, r.stderr
    assert "健全" in r.stdout
    assert "filled: 1" in r.stdout
