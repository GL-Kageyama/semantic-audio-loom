"""mix（シーン合成）の純関数テスト。

`mix_cues` が複数キューを「間（無音）」で正しく連結することを検証する。normalize と
同じく numpy のみに依存し、Provider は使わない。
"""
from __future__ import annotations

import numpy as np

from semantic_audio_loom.engine.mix import mix_cues, silence


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
