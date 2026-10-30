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


def measure(path: str) -> dict:
    """1 ファイルを測る。数値だけを返す（文言は CLI 側）。"""
    arr, sr, ch, width = read_wav(path)
    mono = arr.mean(axis=1) if arr.ndim > 1 else arr
    n = int(mono.shape[0])
    duration = n / float(sr) if sr else 0.0
    peak = float(np.max(np.abs(mono))) if n else 0.0
    rms = float(np.sqrt(np.mean(mono ** 2))) if n else 0.0
    silent = float(np.mean(np.abs(mono) < 10 ** (_SILENT_DBFS / 20.0))) if n else 1.0
    clipped = int(np.sum(np.abs(mono) >= _CLIP_LEVEL))

    centroid = 0.0
    flatness = 0.0
    bands = {name: 0.0 for name in ("low", "mid", "high")}
    if n >= 1024:
        size = min(8192, n)
        spec = np.abs(np.fft.rfft(mono[:size] * np.hanning(size)))
        freqs = np.fft.rfftfreq(size, 1.0 / sr)
        power = spec ** 2
        total = float(power.sum()) + 1e-12
        centroid = float((power * freqs).sum() / total)
        flatness = float(np.exp(np.mean(np.log(power + 1e-12))) / (power.mean() + 1e-12))
        for name, (lo, hi) in (("low", _LOW_BAND), ("mid", _MID_BAND), ("high", _HIGH_BAND)):
            sel = (freqs >= lo) & (freqs < hi)
            bands[name] = 10.0 * float(np.log10(float(power[sel].sum()) / total + 1e-12))

    head_step = float(abs(float(mono[0]))) if n else 0.0

    flags = []
    if rms <= 10 ** (_SILENT_DBFS / 20.0):
        flags.append(("silent", {"rms_db": round(_db(rms), 1)}))
    if clipped:
        flags.append(("clipped", {"count": clipped}))
    if bands["low"] - bands["mid"] > 12.0:
        flags.append(("bass_heavy", {"diff_db": round(bands["low"] - bands["mid"], 1)}))
    if bands["high"] < -45.0:
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
        "clipped": clipped,
        "centroid_hz": round(centroid, 1),
        "flatness": round(flatness, 4),
        "bands_db": {k: round(v, 1) for k, v in bands.items()},
        "flags": flags,
    }
