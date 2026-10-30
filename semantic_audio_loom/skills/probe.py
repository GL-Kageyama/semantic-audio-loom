"""生成した音の診断（耳の代わりに測る）。

音を聴かずに「おかしい」の候補を数で見るための計測。良し悪しは判定しない
（曲が暗いのは趣味のこともある）。出すのは事実だけで、注意を促すのは
機械的に明らかな欠陥（無音・クリップ・高域の完全な欠落・先頭の段差）に限る。
"""
from __future__ import annotations

import wave

import numpy as np

_SILENT_DBFS = -50.0      # これ未満は実質無音
_CLIP_LEVEL = 0.999       # これを超えるサンプルをクリップと数える
_LOW_BAND = (20.0, 250.0)
_MID_BAND = (250.0, 2000.0)
_HIGH_BAND = (2000.0, 16000.0)
_HEAD_STEP = 0.01
_FFT_SIZE = 8192          # 1 フレームの長さ（32kHz で約 0.26 秒）
_MAX_FRAMES = 2000        # 長い音でも計算量を抑える上限


def read_wav(path: str) -> tuple[np.ndarray, int, int, int]:
    """(samples, sample_rate, channels, sample_width_bytes)。samples は (n, ch)。"""
    with wave.open(path) as w:
        sr = w.getframerate()
        ch = w.getnchannels()
        width = w.getsampwidth()
        raw = w.readframes(w.getnframes())
    if width == 1:  # 8bit は符号なし
        arr = (np.frombuffer(raw, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
    elif width == 2:
        arr = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    elif width == 4:
        arr = np.frombuffer(raw, dtype=np.int32).astype(np.float32) / 2147483648.0
    else:
        raise ValueError(f"unsupported sample width: {width} bytes")
    if ch > 1:
        arr = arr.reshape(-1, ch)
    return arr, sr, ch, width


def _db(value: float) -> float:
    return 20.0 * float(np.log10(max(value, 1e-12)))


def _average_spectrum(mono: np.ndarray, sr: int) -> tuple[np.ndarray, np.ndarray] | None:
    """全長を覆う窓の平均パワースペクトル。(power, freqs) を返す。

    先頭の 0.2 秒だけを測ると、曲ではなく「立ち上がりの一瞬」を測ってしまう。
    打楽器の曲は先頭の 1 拍で低域に、爪弾きは先頭のアタックで高域に寄り、
    同じプロンプトでも seed ごとに帯域の判定が反転する。窓は全体へ散らす。
    """
    n = int(mono.shape[0])
    size = _FFT_SIZE if n >= _FFT_SIZE else 1 << max(int(np.log2(max(n, 2))), 1)
    if size < 256:
        return None
    win = np.hanning(size)
    hop = size // 2
    starts = list(range(0, n - size + 1, hop)) or [0]
    if len(starts) > _MAX_FRAMES:  # 長い音は等間隔に間引く
        stride = int(np.ceil(len(starts) / _MAX_FRAMES))
        starts = starts[::stride]
    acc = np.zeros(size // 2 + 1)
    count = 0
    for start in starts:
        seg = mono[start:start + size]
        if seg.shape[0] < size:
            seg = np.pad(seg, (0, size - seg.shape[0]))
        if not np.all(np.isfinite(seg)):
            continue
        acc += np.abs(np.fft.rfft(seg * win)) ** 2
        count += 1
    if not count:
        return None
    return acc / count, np.fft.rfftfreq(size, 1.0 / sr)


def _burst_db(mono: np.ndarray, sr: int) -> float | None:
    """10ms 包絡の (最大 − 中央値) dB。一点で鳴る音ほど大きい。

    帯域と重心は「何が鳴っているか」しか言わない。持続音（ヒス・パッド）も
    クリックも「高域が多い」と答えるので、sfx が点で鳴ったかは別に測る。
    目安：クリック・打撃は 15 dB 以上、連続音は数 dB。
    """
    hop = max(1, int(round(0.01 * sr)))
    n = (mono.shape[0] // hop) * hop
    if n < hop * 2:
        return None
    frames = mono[:n].reshape(-1, hop).astype(np.float64)
    env = np.sqrt(np.mean(frames**2, axis=1) + 1e-12)
    db = 20.0 * np.log10(env + 1e-12)
    return float(db.max() - np.median(db))


def measure(path: str) -> dict:
    """1 ファイルを測る。数値だけを返す（文言は CLI 側）。"""
    arr, sr, ch, width = read_wav(path)
    mono = arr.mean(axis=1) if arr.ndim > 1 else arr
    n = int(mono.shape[0])
    duration = n / float(sr) if sr else 0.0
    # 量（peak / RMS / クリップ）は全チャンネルで測る。モノラルへ落としてから
    # 測ると、左右の相関が低い音ほど小さい値になる（相関 0.25 の sfx で
    # peak 0.95 → 0.69、RMS −3 dB）。波形そのものの量でない数を報告しない。
    flat = arr.reshape(-1) if arr.ndim > 1 else mono
    peak = float(np.max(np.abs(flat))) if n else 0.0
    rms = float(np.sqrt(np.mean(flat ** 2))) if n else 0.0
    silent = float(np.mean(np.abs(mono) < 10 ** (_SILENT_DBFS / 20.0))) if n else 1.0
    clipped = int(np.sum(np.abs(flat) >= _CLIP_LEVEL))

    centroid = None
    flatness = None
    bands = {name: None for name in ("low", "mid", "high")}
    spectrum = _average_spectrum(mono, sr) if n else None
    if spectrum is not None:
        power, freqs = spectrum
        total = float(power.sum()) + 1e-12
        centroid = float((power * freqs).sum() / total)
        flatness = float(np.exp(np.mean(np.log(power + 1e-12))) / (power.mean() + 1e-12))
        for name, (lo, hi) in (("low", _LOW_BAND), ("mid", _MID_BAND), ("high", _HIGH_BAND)):
            sel = (freqs >= lo) & (freqs < hi)
            bands[name] = 10.0 * float(np.log10(float(power[sel].sum()) / total + 1e-12))

    head_step = float(abs(float(mono[0]))) if n else 0.0
    burst = _burst_db(mono, sr) if n else None

    flags = []
    if n and spectrum is None:
        flags.append(("too_short", {"samples": n}))
    if rms <= 10 ** (_SILENT_DBFS / 20.0):
        flags.append(("silent", {"rms_db": round(_db(rms), 1)}))
    if clipped:
        flags.append(("clipped", {"count": clipped}))
    if bands["low"] is not None and bands["mid"] is not None \
            and bands["low"] - bands["mid"] > 12.0:
        flags.append(("bass_heavy", {"diff_db": round(bands["low"] - bands["mid"], 1)}))
    if bands["high"] is not None and bands["high"] < -45.0:
        flags.append(("no_highs", {"level_db": round(bands["high"], 1)}))
    if head_step > _HEAD_STEP:
        flags.append(("head_step", {"value": round(head_step, 3)}))

    return {
        "path": path,
        "duration": round(duration, 3),
        "sample_rate": sr,
        "channels": ch,
        "bits": width * 8,
        "peak": round(peak, 4),
        "rms_db": round(_db(rms), 1),
        "crest_db": round(_db(peak) - _db(rms), 1),
        "dc": round(float(mono.mean()), 5) if n else 0.0,
        "silent_fraction": round(silent, 4),
        "burst_db": round(burst, 1) if burst is not None else None,
        "clipped": clipped,
        # 測れない（短すぎる）ときは 0.0 を返さない。0 dB は「無い」ではなく
        # 「全体と同じ」に見えてしまう。
        "centroid_hz": round(centroid, 1) if centroid is not None else None,
        "flatness": round(flatness, 4) if flatness is not None else None,
        "bands_db": {k: (round(v, 1) if v is not None else None) for k, v in bands.items()},
        "flags": flags,
    }
