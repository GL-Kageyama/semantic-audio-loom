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
    assert spec["prompt"] == (
        "An understated solo piano piece, lonely, slow. About 20 seconds."
    )
    assert spec["duration"] == 20


def test_music_prompt_describes_the_sound_not_the_metadata():
    """60 BPM や role 名を並べない。MusicGen は音の説明文で条件づけされる。"""
    spec = resolve.resolve_music_rule(
        sound.build_intent(
            "bgm",
            {
                "role": "underscore",
                "mood": ["lonely", "still"],
                "instrumentation": ["felt piano"],
                "tempo": {"bpm": 60},
            },
        )
    )
    prompt = spec["prompt"]
    assert prompt.startswith("An understated felt piano piece")
    assert "lonely and still" in prompt
    assert "BPM" not in prompt
    assert "no vocals" not in prompt
    assert "background score" not in prompt


def test_music_prompt_uses_style_when_there_is_no_instrument():
    spec = resolve.resolve_music_rule(
        sound.build_intent("bgm", {"style": ["lofi"], "tempo": {"bpm": 150}})
    )
    assert spec["prompt"] == "A lofi piece, fast"


def test_music_prompt_without_material_is_still_a_sentence():
    spec = resolve.resolve_music_rule(sound.build_intent("bgm", {}))
    assert spec["prompt"] == "A piece of music"


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


def test_normalize_fades_in_only_when_the_start_is_not_silent():
    # 生成モデルは曲の途中から鳴り始めることがある。t=0 が 0 でない波形は
    # 再生時にプツッと鳴るので、2ms のランプで消す（立ち上がりは鈍らせない）。
    sr = 44100
    loud = np.full(sr // 10, 0.5, dtype=np.float32)
    out = normalize.normalize(Audio(wav=loud, sample_rate=sr), tail_fade_ms=None)
    assert abs(float(out.wav[0])) < 1e-3
    n = int(sr * normalize.FADE_IN_MS / 1000.0)
    assert float(out.wav[n]) == pytest.approx(0.95, abs=1e-3)  # ランプの後は元の振幅

    # 先頭がごく小さい（＝自然に立ち上がる）波形は、正規化しても先頭は小さいまま。
    quiet = np.concatenate([np.full(20, 0.001, dtype=np.float32),
                            np.full(sr // 10, 0.5, dtype=np.float32)])
    out = normalize.normalize(Audio(wav=quiet, sample_rate=sr), tail_fade_ms=None)
    assert float(out.wav[0]) == pytest.approx(0.0019, abs=1e-3)  # 静かな始まりには触らない

    off = normalize.normalize(Audio(wav=loud, sample_rate=sr), tail_fade_ms=None,
                              head_fade_ms=None)
    assert float(off.wav[0]) == pytest.approx(0.95, abs=1e-3)


def test_engine_head_fades_sound_but_not_voice():
    # 声は既存の音を変えない（head fade は音の 4 種だけ）。
    from semantic_audio_loom.types import GenerationRequest

    eng = AudioAssetEngine(provider_name="stub", resolve_mode="rule")
    loud = Audio(wav=np.full(24000, 0.5, dtype=np.float32), sample_rate=24000)

    voice = eng._normalize(
        GenerationRequest(asset_type="voice", spec={}, seed=1,
                          voice_profile=_VOICE_PROFILE, dialogue="あ", reading="あ", duration=1.0),
        loud,
    )
    assert float(np.abs(voice.wav[0])) > 0.1  # 触っていない

    sfx = eng._normalize(
        GenerationRequest(asset_type="sfx", spec={"kind": "sfx"}, seed=1, duration=1.0),
        Audio(wav=np.full(44100, 0.5, dtype=np.float32), sample_rate=44100),
    )
    assert float(np.abs(sfx.wav[0])) < 1e-3  # 先頭はランプで 0 から


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


# ---------------------------------------------------------------- プロンプトは英語


def _has_cjk(text: str) -> bool:
    return any(
        0x3040 <= ord(c) <= 0x30FF or 0x4E00 <= ord(c) <= 0x9FFF for c in text
    )


def test_music_rule_keeps_japanese_situation_out_of_prompt():
    # 生成モデル（T5）は英語で学習している。日本語の状況は subtext に残し、
    # モデル向けプロンプトには混ぜない。
    intent = sound.build_intent(
        "bgm",
        {"role": "underscore", "mood": ["lonely"], "instrumentation": ["felt piano"],
         "duration": 10},
        situation="深夜の部屋。窓の外は雨。",
    )
    spec = resolve.resolve_music_rule(intent)
    assert not _has_cjk(spec["prompt"])
    assert spec["subtext"] == "深夜の部屋。窓の外は雨。"


def test_music_rule_appends_english_situation_without_double_period():
    intent = sound.build_intent(
        "bgm", {"role": "underscore", "mood": ["calm"], "duration": 30},
        situation="A rainy window at midnight.",
    )
    prompt = resolve.resolve_music_rule(intent)["prompt"]
    assert prompt.endswith("About 30 seconds. Scene: A rainy window at midnight.")
    assert ".." not in prompt


def test_rule_warns_when_prompt_is_not_english(capsys):
    intent = sound.build_intent("sfx", {"event": "門が閉まる", "duration": 2})
    spec = resolve.resolve(intent, mode="rule", lang="ja")
    assert spec["prompt"]  # 捨てはしない
    err = capsys.readouterr().err
    assert "非英語" in err


# ---------------------------------------------------------------- Provider


def test_duration_over_limit_is_reported_not_silent():
    """上限で切るなら切ったと言う（依頼どおりの尺の資材に見せない）。"""
    from semantic_audio_loom.engine import route

    provider = route.route("bgm", "musicgen")
    assert route.duration_warning(provider, 10, "ja") is None
    assert route.duration_warning(provider, None, "ja") is None
    warning = route.duration_warning(provider, 60, "ja")
    assert warning is not None
    assert "60" in warning and "30" in warning and "musicgen" in warning


def test_engine_warns_when_duration_exceeds_provider(capsys):
    from semantic_audio_loom.engine.engine import AudioAssetEngine

    eng = AudioAssetEngine(provider_name="stub", resolve_mode="rule", lang="ja")
    eng.generate(
        GenerationIntent(
            asset_type="ambience",
            sound={"environment": "rain", "duration": 60, "loop": {"enabled": True}},
        )
    )
    assert "上限" in capsys.readouterr().err


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
