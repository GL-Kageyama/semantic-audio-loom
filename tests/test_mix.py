"""mix（シーン合成）の純関数テスト。

`mix_cues` が複数キューを「間（無音）」で正しく連結することを検証する。normalize と
同じく numpy のみに依存し、Provider は使わない。
"""
from __future__ import annotations

import os

import numpy as np

from semantic_audio_loom.engine.mix import duck, mix_cues, overlay, silence


def _wav(n: int, val: float = 0.5) -> np.ndarray:
    return np.full(n, val, dtype=np.float32)


def test_silence_length_and_dtype():
    sr = 24000
    out = silence(0.5, sr)
    assert out.dtype == np.float32
    assert out.shape == (12000,)
    assert float(np.abs(out).max()) == 0.0


def test_silence_zero_and_negative_are_empty():
    assert silence(0.0).size == 0
    assert silence(-1.0).size == 0


def test_mix_cues_concatenates_in_order():
    sr = 24000
    a = _wav(10, 1.0)
    b = _wav(10, 2.0)
    audio = mix_cues([(a, 0.0), (b, 0.0)], sr)
    out = np.asarray(audio.wav)
    assert audio.sample_rate == sr
    assert out.shape == (20,)
    assert float(out[0]) == 1.0
    assert float(out[19]) == 2.0


def test_mix_cues_leading_pause():
    sr = 24000
    a = _wav(10, 1.0)
    audio = mix_cues([(a, 0.5)], sr)
    out = np.asarray(audio.wav)
    assert out.shape == (12010,)
    assert float(np.abs(out[:12000]).max()) == 0.0
    assert float(out[12000]) == 1.0


def test_mix_cues_pause_between_cues():
    sr = 24000
    a = _wav(10, 1.0)
    b = _wav(10, 2.0)
    audio = mix_cues([(a, 0.0), (b, 0.5)], sr)
    out = np.asarray(audio.wav)
    assert out.shape == (12020,)
    assert float(out[9]) == 1.0
    assert float(np.abs(out[10:12010]).max()) == 0.0  # 間（無音）
    assert float(out[12010]) == 2.0


def test_mix_cues_empty_is_empty():
    audio = mix_cues([], 24000)
    assert np.asarray(audio.wav).size == 0
    assert audio.sample_rate == 24000


# ---------------------------------------------------------------- 重ね合わせ


def test_overlay_places_tracks_at_their_start_and_gain():
    sr = 24000
    a = _wav(2400, 0.5)          # 0.1 秒
    b = _wav(1200, 0.5)          # 0.05 秒
    audio = overlay([(a, 0.0, 0.0), (b, 0.05, -6.0)], sr)
    out = np.asarray(audio.wav)
    assert out.shape == (2400,)
    assert abs(float(out[100]) - 0.5) < 1e-6          # a だけ
    # b は −6 dB（0.501）で足される
    assert abs(float(out[1500]) - (0.5 + 0.5 * 10 ** (-6 / 20))) < 1e-5


def test_overlay_does_not_clip_or_trim_to_unit_range():
    """天井は Normalize の仕事。ここで切ると歪みが仕様になる。"""
    sr = 24000
    a = _wav(100, 0.9)
    audio = overlay([(a, 0.0, 0.0), (a, 0.0, 0.0)], sr)
    assert float(np.max(np.abs(np.asarray(audio.wav)))) > 1.0


def test_overlay_total_seconds_pads_short_mixes():
    sr = 24000
    audio = overlay([(_wav(100, 0.5), 0.0, 0.0)], sr, total_seconds=1.0)
    assert np.asarray(audio.wav).shape == (24000,)


def test_duck_lowers_the_bed_only_while_the_voice_sounds():
    sr = 24000
    bed = _wav(sr, 0.5)                    # 1 秒の一定音
    voice = np.zeros(sr, dtype=np.float32)
    voice[sr // 2:sr // 2 + 2400] = 0.4    # 真ん中 0.1 秒だけ声（−8 dBFS 相当）
    out = duck(bed, voice, sr, threshold_db=-30.0, depth_db=12.0)
    quiet = float(np.mean(np.abs(out[sr // 2 + 480:sr // 2 + 1920])))
    loud = float(np.mean(np.abs(out[:2400])))
    assert quiet < loud * 0.6, (quiet, loud)          # 声の間は沈む
    assert abs(loud - 0.5) < 1e-3                      # 声の外は素通し
    # 戻りは滑らか（急に戻ると「息継ぎ」に聞こえる）
    after = float(np.mean(np.abs(out[sr // 2 + 3000:sr // 2 + 3500])))
    assert after > quiet
    assert after < 0.5


def test_duck_without_voice_returns_the_bed_unchanged():
    sr = 24000
    bed = _wav(1000, 0.5)
    out = duck(bed, np.zeros(1000, dtype=np.float32), sr)
    assert np.allclose(np.asarray(out), bed, atol=1e-6)


# ---------------------------------------------------------------- CLI（bin/mix.py）


def _write_wav(path, samples, sr=24000):
    import wave

    pcm = (np.clip(np.asarray(samples, dtype=np.float32), -1, 1) * 32767).astype(np.int16)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())
    return str(path)


def test_mix_cli_bundles_three_layers_and_ducks_the_bed(tmp_path):
    """生成せずに、既にある音を束ねる経路。山とファイル名の取り違えをここで見る。"""
    import json
    import subprocess
    import sys

    sr = 24000
    t = np.arange(sr) / sr
    bed = (0.3 * np.sin(2 * np.pi * 220 * t)).astype(np.float32)      # 1 秒
    voice = (0.5 * np.sin(2 * np.pi * 440 * np.arange(2400) / sr)).astype(np.float32)
    hit = (0.8 * np.sin(2 * np.pi * 900 * np.arange(600) / sr)).astype(np.float32)
    for name, wav in (("bed", bed), ("voice", voice), ("hit", hit)):
        _write_wav(tmp_path / f"{name}.wav", wav, sr)

    spec = {
        "sample_rate": sr,
        "output": "mix",
        "stems": [
            {"file": "bed.wav", "role": "bed", "start": 0.0, "gain_db": 0.0},
            {"file": "voice.wav", "role": "voice", "start": 0.2, "gain_db": 0.0},
            {"file": "hit.wav", "role": "hit", "start": 0.5, "gain_db": -6.0},
        ],
    }
    import yaml

    (tmp_path / "mix.yaml").write_text(yaml.safe_dump(spec, allow_unicode=True), encoding="utf-8")
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    proc = subprocess.run(
        [sys.executable, os.path.join(root, "bin", "mix.py"),
         "--file", str(tmp_path / "mix.yaml"), "--out-dir", str(tmp_path), "--json"],
        capture_output=True, text=True, env={**os.environ, "PYTHONPATH": root},
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["roles"] == {"bed": 1, "voice": 1, "hit": 1}
    assert summary["ducked"] is True
    out = np.asarray(__import__("semantic_audio_loom.skills.probe", fromlist=["read_wav"]).read_wav(summary["path"])[0])
    assert out.size == sr  # 最後に鳴り終わるのは bed（1.0 秒）
    assert float(np.max(np.abs(out))) > 0.0


# ---------------------------------------------------------------- チャンネル（定位）


def test_overlay_keeps_stereo_and_puts_mono_in_both_ears():
    """mono の声は両耳の真ん中へ。ステレオの sfx は左右を保つ。

    モノラルへ落として混ぜると、左右の相関が低い音ほど小さくなる
    （相関 0.25 で −2 dB）。利得の指定が聞こえる量とずれる。
    """
    sr = 24000
    mono = _wav(100, 0.5)
    left, right = _wav(100, 0.5), _wav(100, 0.1)
    stereo = np.stack([left, right], axis=1)
    audio = overlay([(mono, 0.0, 0.0), (stereo, 0.0, 0.0)], sr, channels=2)
    out = np.asarray(audio.wav)
    assert out.shape == (100, 2)
    assert np.allclose(out[:, 0], 1.0)          # 0.5（mono・複製）＋ 0.5
    assert np.allclose(out[:, 1], 0.6)          # 0.5（mono・複製）＋ 0.1


def test_duck_lowers_every_channel_by_the_same_amount():
    sr = 24000
    bed = np.stack([_wav(sr, 0.5), _wav(sr, 0.25)], axis=1)
    voice = np.zeros(sr, dtype=np.float32)
    voice[sr // 2:sr // 2 + 2400] = 0.4
    out = np.asarray(duck(bed, voice, sr, threshold_db=-30.0, depth_db=12.0))
    q0 = float(np.mean(np.abs(out[sr // 2 + 480:sr // 2 + 1920, 0])))
    q1 = float(np.mean(np.abs(out[sr // 2 + 480:sr // 2 + 1920, 1])))
    assert abs(q0 / q1 - 2.0) < 0.05           # 左右の比は変わらない（定位が動かない）
    assert q0 < 0.5 * 0.6                      # 声の間は沈む


def test_mix_cli_keeps_stereo_when_a_stem_is_stereo(tmp_path):
    import json
    import subprocess
    import sys

    import yaml

    sr = 24000
    t = np.arange(sr) / sr
    bed = (0.3 * np.sin(2 * np.pi * 220 * t)).astype(np.float32)
    wide = np.stack([bed, -bed], axis=1)      # 左右が逆相＝モノラルで消える音
    _write_wav(tmp_path / "voice.wav", bed, sr)
    import wave

    pcm = (np.clip(wide, -1, 1) * 32767).astype(np.int16)
    with wave.open(str(tmp_path / "wide.wav"), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())

    spec = {"sample_rate": sr, "output": "mix", "stems": [
        {"file": "voice.wav", "role": "voice", "start": 0.0, "gain_db": -12.0},
        {"file": "wide.wav", "role": "hit", "start": 0.0, "gain_db": -12.0},
    ]}
    (tmp_path / "mix.yaml").write_text(yaml.safe_dump(spec, allow_unicode=True), encoding="utf-8")
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    proc = subprocess.run(
        [sys.executable, os.path.join(root, "bin", "mix.py"),
         "--file", str(tmp_path / "mix.yaml"), "--out-dir", str(tmp_path), "--json"],
        capture_output=True, text=True, env={**os.environ, "PYTHONPATH": root},
    )
    assert proc.returncode == 0, proc.stderr
    summary = json.loads(proc.stdout)
    assert summary["channels"] == 2
    from semantic_audio_loom.skills.probe import read_wav

    arr, _, ch, _ = read_wav(summary["path"])
    assert ch == 2
    assert float(np.max(np.abs(arr))) > 0.05
