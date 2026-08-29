"""Normalize（7 段フローの第 5 段）。

声量三層分業の「Mixing（量）」レイヤの最小実装：

- 波形を float32 mono に正規化（downmix + NaN 除去）
- ピークを天井（既定 0.95）へ合わせる（クリップ回避）
- 末尾に短いフェードアウト（語尾のブツ切り＝クリック除去）

「張り（loudness.effort）」はここでは触らない。あくまで再生音量の統一。
LUFS 基準のラウドネス正規化は M3 で（要 pyloudnorm）。

末尾フェードの根拠：Tsukasa（拡散）は release を持たない音素（「る」「た」などの
短母音・促音系）だと最終フレームを有声のまま終端させ、要の一打（文末に置かれる
重要な語）がそのまま切断位置になる。プロンプト（"trailing off"）や rate_of_speech
では直らない（実測）。ここでは余韻そのものは復元できず、クリックだけを消す。
"""
from __future__ import annotations

import numpy as np

from semantic_audio_loom.types import Audio

# 末尾フェードの長さ（ms）。短母音で終わる語の「ブツ切り」のクリックを消す最小値。
# 長くすると全台詞に「ため息で引く」癖が乗るため、de-click に留める。
TAIL_FADE_MS = 30.0


def _tail_fade(wav: np.ndarray, sample_rate: int, ms: float = TAIL_FADE_MS) -> np.ndarray:
    """末尾へ半ハン（余弦）フェードを掛け、有声のまま終端する波形のクリックを消す。

    自然に減衰した波形（末尾が既に無音）には実質 no-op。
    """
    n = int(sample_rate * ms / 1000.0)
    if n <= 0 or wav.size <= n:
        return wav
    wav = wav.copy()
    t = np.linspace(0.0, 1.0, n, endpoint=True)
    fade = 0.5 * (1.0 + np.cos(np.pi * t))  # 1 → 0
    wav[-n:] *= fade
    return wav


def normalize(audio: Audio, ceiling: float = 0.95, tail_fade_ms: float = TAIL_FADE_MS) -> Audio:
    wav = np.asarray(audio.wav, dtype=np.float32).squeeze()
    if wav.ndim != 1:
        wav = wav.mean(axis=0)
    wav = np.nan_to_num(wav, nan=0.0, posinf=0.0, neginf=0.0)
    peak = float(np.max(np.abs(wav))) if wav.size else 0.0
    if peak > 0.0:
        wav = wav * (ceiling / peak)
    wav = _tail_fade(wav, audio.sample_rate, tail_fade_ms)
    return Audio(wav=wav, sample_rate=audio.sample_rate)
