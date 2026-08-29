"""normalize（末尾フェード）のテスト。

Tsukasa の拡散出力が短母音の語尾を release なしで終端させる「ブツ切り」を、
末尾フェードがクリックとして除去できること・自然減衰した波形を壊さないことを検証する。
"""
from __future__ import annotations

import numpy as np

from semantic_audio_loom.engine.normalize import _tail_fade, normalize
from semantic_audio_loom.types import Audio


def _tail_rms(wav: np.ndarray, sr: int, ms: float = 20.0) -> float:
    return float(np.sqrt(np.mean(wav[-int(sr * ms / 1000) :] ** 2)))


def test_tail_fade_removes_click_on_chopped_end():
    sr = 24000
    # 有声のまま終端する波形（末尾がフル振幅で切れる＝ブツ切り）
    wav = np.full(sr, 0.5, dtype=np.float32)  # 1 秒、ずっと 0.5
    out = _tail_fade(wav, sr, ms=30.0)
    n = int(sr * 0.03)
    # 最終サンプルはゼロ＝不連続（クリック）なし。フェード開始点は元の振幅、それ以前は不変。
    assert abs(out[-1]) < 1e-3
    assert out[-n] == 0.5
    assert np.allclose(out[:-n], 0.5)


def test_tail_fade_is_noop_on_silent_tail():
    sr = 24000
    # 自然減衰した波形（末尾 100ms は無音）
    wav = np.full(sr, 0.5, dtype=np.float32)
    wav[-int(sr * 0.1) :] = 0.0
    out = _tail_fade(wav, sr, ms=30.0)
    # 無音部分は既に 0 なので変化なし（no-op）
    assert np.array_equal(out, wav)


def test_normalize_applies_fade_after_peak_normalization():
    sr = 24000
    wav = np.full(sr, 0.5, dtype=np.float32)
    audio = normalize(Audio(wav=wav, sample_rate=sr), ceiling=0.95)
    out = np.asarray(audio.wav)
    # ピーク正規化は残しつつ、末尾がフェードで 0 に落ちる
    assert np.max(np.abs(out)) == 0.95
    assert abs(out[-1]) < 0.01
