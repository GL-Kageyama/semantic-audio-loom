"""Mix（合成）— Scene / Timeline の連結レイヤ（Phase 4 の最小形）。

voice の 7 段フローには入らない、生成済み `Audio` を「間（無音）」で並べる純関数。
`normalize.py` の姉妹モジュールで、numpy のみに依存し Provider は持たない。

環境音・BGM の重ね合わせ、ducking・パン・クロスフェード・LUFS マスター正規化は
将来スコープ（docs/asset-types.md Phase 4 の残り）。
"""
from __future__ import annotations

import numpy as np

from semantic_audio_loom import config
from semantic_audio_loom.types import Audio


def silence(seconds: float, sample_rate: int = config.SAMPLE_RATE) -> np.ndarray:
    """`seconds` 秒の無音（float32 mono のゼロ列）。負値は 0 秒として扱う。"""
    n = max(0, int(round(seconds * sample_rate)))
    return np.zeros(n, dtype=np.float32)


def mix_cues(
    cues: list[tuple[np.ndarray, float]],
    sample_rate: int = config.SAMPLE_RATE,
) -> Audio:
    """キュー波形を「各キューの前の無音（秒）」を挟んで連結する。

    cues は `(wav_float32_mono, pause_before_sec)` の列。先頭キューにも pause_before
    があれば、その分の先頭無音を入れる（明示指定として尊重する）。
    """
    parts: list[np.ndarray] = []
    for wav, pause in cues:
        wav = np.asarray(wav, dtype=np.float32).squeeze()
        if pause > 0.0:
            parts.append(silence(pause, sample_rate))
        parts.append(wav)
    if not parts:
        return Audio(wav=np.zeros(0, dtype=np.float32), sample_rate=sample_rate)
    return Audio(wav=np.concatenate(parts), sample_rate=sample_rate)
