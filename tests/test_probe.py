"""probe（耳の代わりの計測器）の検査。

計測器そのものの欠陥は、音の欠陥より見つけにくい。測った数が正しいかは
「作り物の音」で見る——何 Hz がどこに何秒あるかを此方が決めておいて、
器が同じことを言うか。
"""
import wave

import numpy as np
import pytest

from semantic_audio_loom.skills import probe


def _write(path, samples, sr=32000, channels=1):
    arr = np.asarray(samples, dtype=np.float32)
    pcm = np.clip(arr * 32767.0, -32768, 32767).astype(np.int16)
    with wave.open(str(path), "w") as w:
        w.setnchannels(channels if pcm.ndim == 1 else pcm.shape[1])
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())
    return str(path)


def _tone(freq, seconds, sr=32000, amp=0.5):
    t = np.arange(int(seconds * sr)) / sr
    return amp * np.sin(2 * np.pi * freq * t)


def test_spectrum_covers_the_whole_file_not_just_the_head(tmp_path):
    """先頭 0.3 秒だけが低音で、残りが高音の音。曲は高音だと言えなければならない。

    先頭の窓だけを見ると「100 Hz の曲」と答える。それは曲ではなく立ち上がりを
    測っている（bass_heavy / no_highs が seed ごとに入れ替わった原因）。
    """
    sr = 32000
    head = _tone(100.0, 0.3, sr)
    tail = _tone(440.0, 2.7, sr)
    path = _write(tmp_path / "head-low.wav", np.concatenate([head, tail]))
    m = probe.measure(path)
    assert m["centroid_hz"] > 300.0, m          # 先頭だけなら 100 Hz 付近になる
    assert m["bands_db"]["mid"] > m["bands_db"]["low"], m
    assert not any(f[0] == "bass_heavy" for f in m["flags"]), m["flags"]


def test_steady_tone_is_measured_the_same_at_both_ends(tmp_path):
    path = _write(tmp_path / "tone.wav", _tone(440.0, 2.0))
    m = probe.measure(path)
    # 440 Hz は中域（250–2000）にあり、重心もその近くに出る
    assert 300.0 < m["centroid_hz"] < 600.0, m
    assert m["bands_db"]["mid"] > m["bands_db"]["high"], m


def test_bass_heavy_tone_is_flagged(tmp_path):
    path = _write(tmp_path / "bass.wav", _tone(60.0, 2.0))
    m = probe.measure(path)
    assert any(f[0] == "bass_heavy" for f in m["flags"]), m["flags"]


def test_too_short_file_reports_no_bands_instead_of_zeros(tmp_path):
    """0.0 dB は「測れない」に見えない。帯域は None、注意は too_short。"""
    path = _write(tmp_path / "blip.wav", _tone(440.0, 0.002))
    m = probe.measure(path)
    assert m["bands_db"] == {"low": None, "mid": None, "high": None}, m
    assert any(f[0] == "too_short" for f in m["flags"]), m["flags"]


def test_clip_and_silence_are_flagged(tmp_path):
    loud = np.clip(_tone(220.0, 1.0, amp=1.5), -1.0, 1.0)
    m = probe.measure(_write(tmp_path / "clip.wav", loud))
    assert any(f[0] == "clipped" for f in m["flags"]), m["flags"]

    m = probe.measure(_write(tmp_path / "quiet.wav", np.zeros(32000)))
    assert any(f[0] == "silent" for f in m["flags"]), m["flags"]


def test_stereo_is_downmixed(tmp_path):
    sr = 32000
    pair = np.stack([_tone(440.0, 1.0, sr), _tone(440.0, 1.0, sr)], axis=1)
    path = _write(tmp_path / "st.wav", pair, channels=2)
    m = probe.measure(path)
    assert m["channels"] == 2
    assert 300.0 < m["centroid_hz"] < 600.0, m


def test_antiphase_stereo_is_not_read_as_silence(tmp_path):
    """左右が逆相の音は、モノラルへ落とすと 0 になる。波形は 0 ではない。

    peak / RMS / クリップは全チャンネルで測る（相関の低い sfx を −3 dB・
    peak 0.69 と報告していた）。帯域と重心はモノラルで測ってよい。
    """
    sr = 32000
    left = _tone(440.0, 1.0, sr, amp=0.5)
    pair = np.stack([left, -left], axis=1)
    m = probe.measure(_write(tmp_path / "antiphase.wav", pair, channels=2))
    assert m["peak"] > 0.4, m
    assert m["rms_db"] > -15.0, m
    assert not any(f[0] == "silent" for f in m["flags"]), m["flags"]


def test_burst_separates_a_click_from_steady_hiss(tmp_path):
    """帯域と重心は「鳴っている」ことしか言わない。点で鳴ったかは包絡で測る。

    クリックを「持続音」と数えると、sfx の欠陥が緑のまま通る。
    """
    sr = 32000
    click = np.zeros(sr, dtype=np.float32)
    click[: 40] = 0.9                      # 1.25 ms の 1 発
    hiss = (np.random.default_rng(0).normal(0, 0.05, sr)).astype(np.float32)
    m_click = probe.measure(_write(tmp_path / "click.wav", click, sr))
    m_hiss = probe.measure(_write(tmp_path / "hiss.wav", hiss, sr))
    assert m_click["burst_db"] > 20.0, m_click
    assert m_hiss["burst_db"] < 10.0, m_hiss
