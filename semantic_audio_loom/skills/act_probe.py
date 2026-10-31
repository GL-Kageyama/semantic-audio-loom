"""演技を測る（台詞 1 本を演技の言葉で測る）。

`probe.py` は音の物理（帯域・重心・起伏・無音率）しか見ない。演技——声の高さ、
抑揚の幅、語尾の上げ下げ、速さ、間、張り、出だしの勢い——は測れない。
ここはその不足を埋める計器で、良し悪しは判定しない。**どの感情がどの指標に
乗ったか**を数で言えるようにするためだけのもの。

定義（値の意味を後から検算できるように書く）：

- `f0_median` … 有声フレームの基本周波数の中央値（Hz）。pyin（librosa）で推定。
- `f0_range_st` … 有声 f0 の 5〜95 パーセンタイルの幅を半音で表したもの。
  抑揚の大きさ。半音 = 12·log2(p95/p5)。
- `f0_end_st_s` … **100ms 以上続いた最後の有声区間**の末尾 200ms の f0 の傾き
  （半音/秒、中央値からの相対）。語尾が上がっているか下がっているか。
  測れる区間が無ければ None。
- `rate_mora_s` … 鳴っている時間あたりの拍（モーラ概算）。10ms 包絡の山を数え、
  「-50 dBFS 以上の時間」で割る（間は pause_ratio が別に測る）。
- `pause_ratio` … 発話の端から端まで（-50 dBFS を超えた最初と最後の間）のうち
  -50 dBFS 未満のフレームの割合。間の取り方。冒頭・末尾の無音は数えない。
- `energy_median_db` / `energy_range_db` … 10ms 包絡の dB の中央値と p95−p5。
  張りと、張りの起伏。
- `attack_ms` … 最初に -40 dBFS を超えたフレームから、続く 300ms の包絡の
  最大値までの時間。出だしの勢い。
- `voiced_fraction` … 全フレームのうち有声と判定された割合。

閾値は probe.py と揃える（無音 -50 dBFS）。測れないときは 0 を返さず None を返す
（0 は「無い」ではなく「全体と同じ」に見える）。
"""
from __future__ import annotations

import numpy as np

from . import probe as _probe

_SILENT_DBFS = -50.0
_ONSET_DBFS = -40.0
_FMIN = 60.0
_FMAX = 600.0
_HEAD_WINDOW_S = 0.3
_END_WINDOW_S = 0.2
_MIN_VOICED_END = 5
_MIN_SPAN_S = 0.1
_VOICED_PROB = 0.3
_END_GAP_S = 0.03
_MIN_DIST_S = 0.09


def _envelope(mono: np.ndarray, sr: int, frame_s: float = 0.01) -> tuple[np.ndarray, float]:
    """フレーム RMS の dB と、1 フレームの秒数。"""
    hop = max(1, int(round(frame_s * sr)))
    n = (mono.shape[0] // hop) * hop
    if n < hop * 2:
        return np.zeros(0), frame_s
    frames = mono[:n].reshape(-1, hop).astype(np.float64)
    env = np.sqrt(np.mean(frames ** 2, axis=1) + 1e-12)
    return 20.0 * np.log10(env + 1e-12), hop / float(sr)


def _f0_track(mono: np.ndarray, sr: int, fmin: float = _FMIN, fmax: float = _FMAX):
    """pyin で f0 を取る。取れなければ None。

    有声の判定に pyin の `voiced_flag` だけを使わない。声が終わったあとの
    減衰・残響にも flag は立つが、そのフレームの有声確率は 0.02 しかない。
    低確率のフレームを混ぜると、語尾の傾きが +50 半音/秒（1 オクターブ/0.2 秒）
    のような物理的にありえない値になる。確率 `_VOICED_PROB` 以上だけを声とする。
    """
    try:
        import librosa
    except Exception:  # librosa が無い環境では f0 系を測らない
        return None, None, None
    hop = max(1, int(round(0.01 * sr)))
    try:
        f0, voiced, prob = librosa.pyin(
            mono.astype(np.float32), fmin=fmin, fmax=fmax, sr=sr,
            frame_length=2048, hop_length=hop)
    except Exception:
        return None, None, None
    prob = np.nan_to_num(prob)
    voiced = voiced & (prob >= _VOICED_PROB) & np.isfinite(f0)
    times = np.arange(f0.shape[0]) * (hop / float(sr))
    return f0, voiced, times


def _track_two_pass(mono: np.ndarray, sr: int):
    """1 回目で声の高さの当たりを付け、2 回目で 1 オクターブの幅に絞って取り直す。

    60〜600 Hz のまま取ると、声の終わりで 1 オクターブ下（350→220 Hz）を掴む
    ことがある。オクターブ誤りは語尾の傾きを 1 オクターブ/0.2 秒にする。
    声の高さは台詞 1 本の中で 1 オクターブを超えて動かないので、中央値の
    上下 1 オクターブへ範囲を狭めれば、誤りは範囲の外へ落ちる。
    """
    f0, voiced, times = _f0_track(mono, sr)
    if f0 is None:
        return f0, voiced, times
    med = np.median(f0[voiced]) if np.any(voiced) else None
    if med is None or not np.isfinite(med) or med <= 0:
        return f0, voiced, times
    fmin = max(40.0, float(med) / 2.0)
    fmax = min(1200.0, float(med) * 2.0)
    f0b, voicedb, timesb = _f0_track(mono, sr, fmin=fmin, fmax=fmax)
    if f0b is None or not np.any(voicedb):
        return f0, voiced, times
    return f0b, voicedb, timesb


def _end_slope(f0, voiced, times, median_hz: float) -> float | None:
    """最後の**連続した**有声区間の末尾 200ms に直線を当て、半音/秒で返す。

    ファイル末尾の 200ms を使うと、TTS の後ろに付く無音を測ってしまい
    どの感情でも None になる。かといって間をまたいで直線を引くと、間の前後の
    別の音節を 1 本の傾きに混ぜてしまう（350 Hz→220 Hz の飛びが
    −54 半音/秒になる）。最後の息継ぎから後ろだけを見る。
    """
    if f0 is None or median_hz is None or median_hz <= 0:
        return None
    idx = np.where(voiced & np.isfinite(f0))[0]
    if idx.size < _MIN_VOICED_END:
        return None
    # 後ろから、30ms を超える切れ目に当たるまで遡り、100ms 以上続く区間を選ぶ。
    # 最後の音節が 50ms しかない（TTS の語尾は短く弱い）ときは、その 1 つ前の
    # 区間が「最後に続いた声」になる。50ms の傾きはノイズなので測らない。
    runs = []
    k = 0
    while k < idx.size:
        j = k
        while j + 1 < idx.size and (times[idx[j + 1]] - times[idx[j]]) <= _END_GAP_S:
            j += 1
        runs.append(idx[k:j + 1])
        k = j + 1
    run = None
    for r in reversed(runs):
        if r.size >= _MIN_VOICED_END and (times[r[-1]] - times[r[0]]) >= _MIN_SPAN_S:
            run = r
            break
    if run is None:
        return None
    end = float(times[run[-1]])
    sel = run[times[run] >= end - _END_WINDOW_S]
    if sel.size < _MIN_VOICED_END:
        return None
    t = times[sel]
    if float(t[-1] - t[0]) < _MIN_SPAN_S:  # 窓が短すぎる傾きはノイズ
        return None
    t = times[sel]
    st = 12.0 * np.log2(f0[sel] / median_hz)
    slope = float(np.polyfit(t - t.mean(), st, 1)[0])
    return slope


def _nuclei(db: np.ndarray, frame_s: float) -> int:
    """10ms 包絡の山を数える（モーラ概算）。"""
    if db.size < 3:
        return 0
    smooth = np.convolve(db, np.ones(3) / 3.0, mode="same")
    thr = max(float(np.percentile(smooth, 75)) - 20.0, _SILENT_DBFS)
    gap = max(1, int(round(_MIN_DIST_S / frame_s)))
    count = 0
    last = -gap
    for i in range(1, smooth.size - 1):
        if smooth[i] < thr:
            continue
        if smooth[i] < smooth[i - 1] or smooth[i] < smooth[i + 1]:
            continue
        if i - last < gap:
            # 近すぎる山は大きいほうを残す
            continue
        count += 1
        last = i
    return count


def _attack_ms(db: np.ndarray, frame_s: float) -> float | None:
    above = np.where(db >= _ONSET_DBFS)[0]
    if above.size == 0:
        return None
    onset = int(above[0])
    head = db[onset:onset + max(1, int(round(_HEAD_WINDOW_S / frame_s)))]
    if head.size == 0:
        return None
    peak = onset + int(np.argmax(head))
    return round((peak - onset) * frame_s * 1000.0, 1)


def measure(path: str) -> dict:
    """台詞 1 本を演技の指標で測る。物理量は probe.measure と揃える。"""
    base = _probe.measure(path)
    arr, sr, _ch, _w = _probe.read_wav(path)
    mono = arr.mean(axis=1) if arr.ndim > 1 else arr
    mono = np.asarray(mono, dtype=np.float64)
    n = int(mono.shape[0])
    duration = n / float(sr) if sr else 0.0

    db, frame_s = _envelope(mono, sr)
    f0, voiced, times = _track_two_pass(mono, sr)

    # 発話の端から端（-50 dBFS を超えた最初と最後）。速さと間の分母。
    span_s = None
    if db.size:
        loud = np.where(db >= _SILENT_DBFS)[0]
        if loud.size >= 2:
            span_s = float((loud[-1] - loud[0] + 1) * frame_s)

    f0_median = None
    f0_range_st = None
    voiced_fraction = None
    end_slope = None
    if f0 is not None and voiced is not None:
        voiced_fraction = round(float(np.mean(voiced)), 4)
        voiced_f0 = f0[voiced & np.isfinite(f0)]
        if voiced_f0.size:
            f0_median = float(np.median(voiced_f0))
            p5, p95 = np.percentile(voiced_f0, [5, 95])
            if p5 > 0:
                f0_range_st = float(12.0 * np.log2(p95 / p5))
        end_slope = _end_slope(f0, voiced, times, f0_median)

    pause_ratio = None
    if db.size:
        loud = np.where(db >= _SILENT_DBFS)[0]
        if loud.size >= 2:
            span = db[int(loud[0]):int(loud[-1]) + 1]
            pause_ratio = float(np.mean(span < _SILENT_DBFS))

    # 張りは「声が出ている間」の量。無音を含めると範囲が 100 dB を超え、
    # 感情の差ではなく「間の長さ」を測ってしまう。
    if voiced is not None and db.size == len(voiced):
        span_db = db[voiced]
    elif db.size:
        span_db = db[db >= _SILENT_DBFS]
    else:
        span_db = db
    energy_median = float(np.median(span_db)) if span_db.size else None
    energy_range = float(np.percentile(span_db, 95) - np.percentile(span_db, 5)) if span_db.size else None

    # 速さの分母は「鳴っている時間」（-50 dBFS 以上）。発話の端から端で割ると
    # 間の長さが混ざり、有声時間で割ると声の切れ目が混ざる。間は pause_ratio が
    # 別に測るので、ここは調音の速さだけを見る。
    sounding_s = float(np.sum(db >= _SILENT_DBFS)) * frame_s if db.size else None
    rate = None
    if sounding_s and sounding_s >= 0.3:
        rate = _nuclei(db, frame_s) / sounding_s

    voiced_s = (float(np.sum(voiced)) * frame_s) if voiced is not None else None

    out = dict(base)
    out.update({
        "f0_median_hz": round(f0_median, 1) if f0_median is not None else None,
        "f0_range_st": round(f0_range_st, 1) if f0_range_st is not None else None,
        "f0_end_st_s": round(end_slope, 2) if end_slope is not None else None,
        "rate_mora_s": round(rate, 1) if rate is not None else None,
        "pause_ratio": round(pause_ratio, 3) if pause_ratio is not None else None,
        "energy_median_db": round(energy_median, 1) if energy_median is not None else None,
        "energy_range_db": round(energy_range, 1) if energy_range is not None else None,
        "attack_ms": _attack_ms(db, frame_s) if db.size else None,
        "voiced_fraction": voiced_fraction,
        "voiced_s": round(voiced_s, 2) if voiced_s is not None else None,
        "span_s": round(span_s, 2) if span_s is not None else None,
    })
    return out


COLUMNS = [
    "path", "duration", "f0_median_hz", "f0_range_st", "f0_end_st_s", "rate_mora_s",
    "pause_ratio", "energy_median_db", "energy_range_db", "attack_ms",
    "voiced_fraction", "peak", "rms_db", "clipped",
]
