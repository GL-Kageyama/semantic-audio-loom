"""Normalize（7 段フローの第 5 段）。

声量三層分業の「Mixing（量）」レイヤの最小実装：

- 波形を float32 へ（NaN 除去。mono は 1 次元、多チャンネルは (n, ch)）
- 目標サンプルレートへリサンプル（既定はそのまま）
- 目標チャンネル数へ変換（voice は mono 固定、音楽・効果音は生成のまま）
- ピークを天井（既定 0.95）へ合わせる（クリップ回避）
- 末尾に短いフェードアウト（語尾のブツ切り・クリック除去）

「張り（loudness.effort）」はここでは触らない。あくまで再生音量の統一。
LUFS 基準のラウンドネス正規化は M6（要 pyloudnorm）。

末尾フェードの根拠：Tsukasa（拡散）は release を持たない音素（「る」「た」などの
短母音・促音系）だと最終フレームを有声のまま終端させ、要の一打（文末に置かれる
重要な語）がそのまま切断位置になる。プロンプト（"trailing off"）や rate_of_speech
では直らない（実測）。ここでは余韻そのものは復元できず、クリックだけを消す。

ループする資材（ambience / loop 指定の bgm）は末尾フェードを掛けない。
掛けるとループの継ぎ目に無音ができる。
"""
from __future__ import annotations

import numpy as np

from semantic_audio_loom.types import Audio

# 末尾フェードの長さ（ms）。短母音で終わる語の「ブツ切り」のクリックを消す最小値。
# 長くすると全台詞に「ため息で引く」癖が乗るため、de-click に留める。
TAIL_FADE_MS = 30.0
# 短い効果音の末尾は 30ms では長すぎる。10ms でクリックだけ消す。
SFX_TAIL_FADE_MS = 10.0


def _as_float(wav) -> np.ndarray:
    arr = np.asarray(wav, dtype=np.float32)
    if arr.ndim == 0:
        arr = arr.reshape(1)
    arr = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)
    if arr.ndim == 1:
        return arr
    if arr.ndim != 2:
        return arr.reshape(-1)
    # (ch, n) と (n, ch) を判別する。チャンネル数は高々 8 程度という前提。
    if arr.shape[0] < arr.shape[1] and arr.shape[0] <= 8:
        return arr.T
    return arr


def _resample(wav: np.ndarray, src: int, dst: int) -> np.ndarray:
    if src == dst or wav.shape[0] == 0:
        return wav
    from fractions import Fraction

    ratio = Fraction(dst, src).limit_denominator(1000)
    try:
        from scipy.signal import resample_poly

        return resample_poly(wav, ratio.numerator, ratio.denominator, axis=0).astype(np.float32)
    except Exception:  # scipy が無い環境向けの線形補間（品質は落ちる）
        n_out = max(1, int(round(wav.shape[0] * dst / src)))
        x = np.arange(wav.shape[0], dtype=np.float64)
        xi = np.linspace(0.0, float(wav.shape[0] - 1), n_out)
        if wav.ndim == 1:
            return np.interp(xi, x, wav).astype(np.float32)
        cols = [np.interp(xi, x, wav[:, c]) for c in range(wav.shape[1])]
        return np.stack(cols, axis=1).astype(np.float32)


def _convert_channels(wav: np.ndarray, channels: int | None) -> np.ndarray:
    if channels is None:
        return wav
    current = 1 if wav.ndim == 1 else wav.shape[1]
    if current == channels:
        return wav
    if channels == 1:
        return wav.mean(axis=1) if wav.ndim == 2 else wav
    if wav.ndim == 1:
        return np.repeat(wav[:, None], channels, axis=1)
    if channels < current:
        return wav[:, :channels]
    pad = np.repeat(wav[:, -1:], channels - current, axis=1)
    return np.concatenate([wav, pad], axis=1)


def _tail_fade(wav: np.ndarray, sample_rate: int, ms: float = TAIL_FADE_MS) -> np.ndarray:
    """末尾へ半ハン（余弦）フェードを掛け、有声のまま終端する波形のクリックを消す。

    自然に減衰した波形（末尾が既に無音）には実質 no-op。
    """
    n = int(sample_rate * ms / 1000.0)
    if n <= 0 or wav.shape[0] <= n:
        return wav
    wav = wav.copy()
    t = np.linspace(0.0, 1.0, n, endpoint=True)
    fade = 0.5 * (1.0 + np.cos(np.pi * t))  # 1 → 0
    if wav.ndim == 1:
        wav[-n:] *= fade
    else:
        wav[-n:] *= fade[:, None]
    return wav


def normalize(
    audio: Audio,
    ceiling: float = 0.95,
    tail_fade_ms: float | None = TAIL_FADE_MS,
    sample_rate: int | None = None,
    channels: int | None = None,
) -> Audio:
    wav = _as_float(audio.wav)
    sr = audio.sample_rate
    if sample_rate and sample_rate != sr:
        wav = _resample(wav, sr, sample_rate)
        sr = sample_rate
    wav = _convert_channels(wav, channels)
    peak = float(np.max(np.abs(wav))) if wav.size else 0.0
    if peak > 0.0:
        wav = (wav * (ceiling / peak)).astype(np.float32)
    if tail_fade_ms:
        wav = _tail_fade(wav, sr, tail_fade_ms)
    return Audio(wav=wav, sample_rate=sr)
