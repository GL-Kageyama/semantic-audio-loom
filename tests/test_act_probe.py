"""act_probe（演技の計器）の検査。

計器は音の欠陥より見つけにくい。作り物の声——f0 を此方が決めた音——を当てて、
器が同じことを言うかを見る。
"""
import wave

import numpy as np

from semantic_audio_loom.skills import act_probe

SR = 16000


def _write(path, samples, sr=SR):
    pcm = np.clip(np.asarray(samples, dtype=np.float32) * 32767.0, -32768, 32767).astype(np.int16)
    with wave.open(str(path), "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())
    return str(path)


def _voiced(seconds, f0, sr=SR, amp=0.4):
    """倍音を 3 本持つ有声らしい音（純音は pyin が拾いにくい）。"""
    t = np.arange(int(seconds * sr)) / sr
    y = np.zeros_like(t)
    for k in range(1, 5):
        y += (amp / k) * np.sin(2 * np.pi * f0 * k * t)
    return y.astype(np.float32)


def test_pitch_and_range_follow_the_signal(tmp_path):
    """200 Hz から 260 Hz へ滑らかに上がる声。中央値も幅も動かなければならない。"""
    seconds = 2.0
    t = np.arange(int(seconds * SR)) / SR
    f0 = 200.0 + (260.0 - 200.0) * (t / seconds)
    phase = 2 * np.pi * np.cumsum(f0) / SR
    y = sum((0.4 / k) * np.sin(k * phase) for k in range(1, 5)).astype(np.float32)
    path = _write(tmp_path / "rising.wav", y)
    e = act_probe.measure(path)
    assert e["f0_median_hz"] is not None
    assert 200.0 <= e["f0_median_hz"] <= 260.0
    # 200→260 Hz は約 4.5 半音。器はそれ以上を主張してはならない。
    assert e["f0_range_st"] is not None
    assert 3.0 <= e["f0_range_st"] <= 8.0
    # 上がっているので語尾の傾きは正
    assert e["f0_end_st_s"] is not None
    assert e["f0_end_st_s"] > 0


def test_ending_slope_is_not_measured_across_a_gap(tmp_path):
    """220 Hz → 無音 200ms → 220 Hz。間をまたいで傾きを作ってはならない。

    前後の別の音節を 1 本の直線に混ぜると、間の分だけ見かけの傾きが大きくなる
    （実測で −54 半音/秒＝1 オクターブ/0.2 秒という物理的にありえない値）。
    """
    gap = np.zeros(int(0.2 * SR), dtype=np.float32)
    y = np.concatenate([_voiced(0.6, 220.0), gap, _voiced(0.6, 220.0)])
    path = _write(tmp_path / "gap-end.wav", y)
    e = act_probe.measure(path)
    assert e["f0_end_st_s"] is None or abs(e["f0_end_st_s"]) < 3.0


def test_steady_pitch_has_no_ending_slope(tmp_path):
    """一定の高さで終わる声の語尾の傾きは 0。上下を作ってはならない。"""
    path = _write(tmp_path / "steady.wav", _voiced(1.5, 220.0))
    e = act_probe.measure(path)
    assert e["f0_end_st_s"] is not None
    assert abs(e["f0_end_st_s"]) < 1.0


def test_pause_ratio_counts_the_gap_not_the_head_or_tail(tmp_path):
    """声 0.5s・無音 0.5s・声 0.5s。間は 3 分の 1 と答えるべき。

    冒頭と末尾の無音まで数えると 5 分の 3 になり、間の取り方を過大に言う。
    """
    gap = np.zeros(int(0.5 * SR), dtype=np.float32)
    y = np.concatenate([_voiced(0.5, 220.0), gap, _voiced(0.5, 220.0)])
    path = _write(tmp_path / "gap.wav", y)
    e = act_probe.measure(path)
    assert e["pause_ratio"] is not None
    assert 0.25 <= e["pause_ratio"] <= 0.42


def test_silence_does_not_inflate_energy_range(tmp_path):
    """無音を張りの幅に混ぜると 100 dB を超える。有声区間だけで測る。"""
    gap = np.zeros(int(1.0 * SR), dtype=np.float32)
    y = np.concatenate([_voiced(0.6, 220.0), gap, _voiced(0.6, 220.0)])
    path = _write(tmp_path / "samples.wav", y)
    e = act_probe.measure(path)
    assert e["energy_range_db"] is not None
    assert e["energy_range_db"] < 40.0


def test_unmeasurable_values_are_none_not_zero(tmp_path):
    """無音しか無い音で 0 Hz と書かない（0 は「無い」ではなく「全体と同じ」に見える）。"""
    path = _write(tmp_path / "silence.wav", np.zeros(SR, dtype=np.float32))
    e = act_probe.measure(path)
    assert e["f0_median_hz"] is None
    assert e["rate_mora_s"] is None
