"""Mix（合成）— Scene / Timeline の連結と重ね合わせのレイヤ（Phase 4）。

voice の 7 段フローには入らない、生成済み `Audio` を「間（無音）」で並べる／
時刻を揃えて重ねる純関数。`normalize.py` の姉妹モジュールで、numpy のみに依存し
Provider は持たない。

層は 3 つ。**bed**（bgm・ambience＝下に流し続ける音）、**voice**（台詞）、
**hit**（sfx・foley＝一点で鳴る音）。bed は voice が鳴っている間だけ下がる（ducking）。
ducking の制御は声の音量そのもので、閾値を超えた分だけ bed を沈める。

チャンネル数はステムの最大に合わせる（mono の声は両耳へ同じに置く）。ステレオの
stem を mono へ落として混ぜると、左右の相関が低い音ほど小さくなる（相関 0.25 で
−2 dB）——利得の指定が聞こえる量とずれる。チャンネル数の指定は `channels`。

クロスフェード・LUFS マスター正規化は将来スコープ（docs/asset-types.md Phase 4 の残り）。
"""
from __future__ import annotations

import numpy as np

from semantic_audio_loom import config
from semantic_audio_loom.types import Audio


def _as_channels(wav: np.ndarray, channels: int) -> np.ndarray:
    """1 次元（mono）か (n, ch) を、目標チャンネル数へ揃える。

    mono → 多チャンネルは複製（同じ音を両耳に置く＝真ん中に定位）。
    多チャンネル → mono は平均。それ以外の変換は先頭から使う。
    """
    wav = np.asarray(wav, dtype=np.float32)
    if wav.ndim == 1:
        return np.repeat(wav[:, None], channels, axis=1) if channels > 1 else wav
    if wav.shape[1] == channels:
        return wav
    if channels == 1:
        return wav.mean(axis=1)
    if wav.shape[1] > channels:
        return wav[:, :channels]
    pad = np.repeat(wav[:, -1:], channels - wav.shape[1], axis=1)
    return np.concatenate([wav, pad], axis=1)


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


def _db_to_gain(db: float) -> float:
    return float(10.0 ** (db / 20.0))


def overlay(
    tracks: list[tuple[np.ndarray, float, float]],
    sample_rate: int = config.SAMPLE_RATE,
    total_seconds: float | None = None,
    channels: int = 1,
) -> Audio:
    """`(wav_float32, start_sec, gain_db)` を時刻を揃えて足す。

    長さは最後の音の終わり（`total_seconds` を与えればその長さ。足りなければ伸ばす）。
    足した結果はクリップしない——天井は Normalize の仕事で、ここで切ると
    歪みを「仕様」にしてしまう。`channels` は揃える先（mono の音は複製して置く）。
    """
    tracks = [(np.asarray(w, dtype=np.float32).squeeze(), float(s), float(g))
              for w, s, g in tracks]
    ends = [s + (len(w) / float(sample_rate)) for w, s, _ in tracks]
    length = max(ends) if ends else 0.0
    if total_seconds is not None:
        length = max(length, float(total_seconds))
    n = max(0, int(round(length * sample_rate)))
    shape = (n,) if channels <= 1 else (n, channels)
    out = np.zeros(shape, dtype=np.float32)
    for wav, start, gain_db in tracks:
        wav = _as_channels(wav, channels)
        i = int(round(start * sample_rate))
        if i >= n or i + len(wav) <= 0:
            continue
        if i < 0:  # 負の開始は先頭を削る
            wav = wav[-i:]
            i = 0
        m = min(len(wav), n - i)
        out[i:i + m] += wav[:m] * _db_to_gain(gain_db)
    return Audio(wav=out, sample_rate=sample_rate)


def _envelope(mono: np.ndarray, sample_rate: int, hop_s: float = 0.005) -> np.ndarray:
    """5ms 刻みの RMS。ducking の制御信号。"""
    hop = max(1, int(round(hop_s * sample_rate)))
    n = (len(mono) // hop) * hop
    if n == 0:
        return np.zeros(1, dtype=np.float32)
    frames = mono[:n].reshape(-1, hop).astype(np.float32)
    return np.sqrt(np.mean(frames ** 2, axis=1) + 1e-12)


def duck(
    bed: np.ndarray,
    control: np.ndarray,
    sample_rate: int = config.SAMPLE_RATE,
    threshold_db: float = -30.0,
    depth_db: float = 10.0,
    attack_s: float = 0.02,
    release_s: float = 0.35,
) -> np.ndarray:
    """control（声）が鳴っている間だけ bed を下げる。

    `threshold_db` を超えた分だけ沈め、沈める量は `depth_db` で頭打ち。立ち上がりは
    `attack_s`、戻りは `release_s` で滑らかにする（戻りを速くすると声の合間に
    bed が「息継ぎ」して聞こえる）。
    """
    bed = np.asarray(bed, dtype=np.float32)
    control = np.asarray(control, dtype=np.float32)
    if bed.size == 0:
        return bed
    if control.ndim > 1:  # 声が多チャンネルでも、制御信号は 1 本でよい
        control = control.mean(axis=1)
    env = _envelope(control, sample_rate)
    level_db = 20.0 * np.log10(env + 1e-9)
    # 声が閾値を超えた分だけ沈める（超えなければ 0 dB、沈みすぎないよう -depth_db で止める）
    reduction = np.clip(level_db - threshold_db, 0.0, None)
    reduction = np.minimum(reduction, depth_db)
    # 速く沈み、ゆっくり戻る非対称の平滑化（5ms 刻みなので単純な一次の追従で足りる）
    a_att = float(np.exp(-0.005 / max(attack_s, 1e-4)))
    a_rel = float(np.exp(-0.005 / max(release_s, 1e-4)))
    smooth = np.empty_like(reduction)
    prev = 0.0
    for i, value in enumerate(reduction):
        a = a_att if value > prev else a_rel
        prev = a * prev + (1.0 - a) * value
        smooth[i] = prev
    # 5ms 刻みの包絡をサンプル単位へ戻す
    positions = np.arange(len(bed), dtype=np.float32) / float(sample_rate) / 0.005
    gain_db = np.interp(positions, np.arange(len(smooth), dtype=np.float32), smooth,
                        left=0.0, right=0.0)
    gain = (10.0 ** (-gain_db / 20.0)).astype(np.float32)
    if bed.ndim > 1:  # 全チャンネルを同じ量だけ下げる（定位は動かさない）
        gain = gain[:, None]
    return bed * gain
