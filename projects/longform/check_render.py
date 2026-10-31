#!/usr/bin/env python
"""仕上げた 1 本を門の数で確かめる（耳の代わりの門番）。

門（計画書）:
- 尺 5 分以上
- 無音の穴・クリップ・ヒス無し
- 効果音は場面の切り目で 15 dB 以上立ち上がる

  PYTHONPATH=. <venv> .../check_render.py projects/longform/assets/explainer/renders/explainer.wav
"""
from __future__ import annotations

import argparse
import sys

import numpy as np

HOP = 0.02
SILENCE_DB = -50.0
BURST_DB = 15.0


def envelope(path: str):
    from semantic_audio_loom.skills.probe import read_wav

    a, sr, ch, _ = read_wav(path)
    a = np.asarray(a, dtype=np.float32)
    if a.ndim > 1:
        a = a.mean(axis=1)
    hop = int(HOP * sr)
    n = len(a) // hop
    rms = np.sqrt((a[: n * hop].reshape(n, hop) ** 2).mean(axis=1) + 1e-12)
    return 20 * np.log10(rms), sr, len(a) / sr


def runs(mask: np.ndarray):
    out, i = [], 0
    while i < len(mask):
        if mask[i]:
            j = i
            while j < len(mask) and mask[j]:
                j += 1
            out.append((i * HOP, (j - i) * HOP))
            i = j
        else:
            i += 1
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("wav")
    ap.add_argument("--min-seconds", type=float, default=300.0)
    ap.add_argument("--mix", default=None, help="mix.yaml（声の区間を除いて効果音だけ測る）")
    args = ap.parse_args()

    db, sr, total = envelope(args.wav)

    # ピークとクリップはサンプルで見る（包絡では丸まる）
    from semantic_audio_loom.skills.probe import read_wav
    a, _sr, _ch, _ = read_wav(args.wav)
    a = np.asarray(a, dtype=np.float32)
    clipped = int((np.abs(a) >= 0.999).sum())
    sample_peak = float(np.abs(a).max())

    sil = db < SILENCE_DB
    gaps = sorted(runs(sil), key=lambda r: -r[1])
    long_gaps = [g for g in gaps if g[1] >= 1.0]

    # 一点の立ち上がり: 直近 1 秒の中央値から 15 dB 上のフレーム
    bursts = []
    win = int(1.0 / HOP)
    for i in range(win, len(db) - win):
        local = np.median(np.concatenate([db[i - win:i], db[i + 1:i + 1 + win]]))
        if db[i] - local >= BURST_DB:
            bursts.append((i * HOP, db[i], db[i] - local))
    # 近接フレームはまとめる
    merged = []
    for t, level, rise in bursts:
        if merged and t - merged[-1][0] < 0.5:
            if rise > merged[-1][2]:
                merged[-1] = (t, level, rise)
        else:
            merged.append((t, level, rise))

    print(f"{args.wav}")
    print(f"  尺        {total:7.1f} s（{total/60:.2f} 分）  門 {args.min_seconds/60:.1f} 分 →",
          "合格" if total >= args.min_seconds else "未達")
    print(f"  ピーク    {20*np.log10(max(sample_peak,1e-9)):7.1f} dBFS / クリップ {clipped}")
    print(f"  無音率    {100*sil.mean():6.1f}%（うち 1 秒以上の穴 {len(long_gaps)} 個）")
    for t, d in long_gaps[:5]:
        print(f"            穴 {t:7.2f}s / {d:4.2f}s")
    # 声の区間を外した立ち上がり＝効果音。声の上では台詞の出だしが全部立つ。
    outside = merged
    n_voice = 0
    if args.mix:
        import os
        import wave

        import yaml

        with open(args.mix, encoding="utf-8") as f:
            spec = yaml.safe_load(f)
        base = os.path.dirname(os.path.abspath(args.mix))
        spans = []
        for stem in spec.get("stems", []):
            if stem.get("role") != "voice":
                continue
            with wave.open(os.path.normpath(os.path.join(base, stem["file"]))) as w:
                d = w.getnframes() / w.getframerate()
            spans.append((float(stem["start"]), float(stem["start"]) + d))
        n_voice = len(spans)
        outside = [b for b in merged
                   if not any(s - 0.05 <= b[0] <= e + 0.05 for s, e in spans)]
        print(f"  声の区間 {n_voice} 本の外で、15 dB 以上の立ち上がり {len(outside)} 個")
    else:
        print(f"  15 dB 以上の立ち上がり {len(merged)} 個（声の中も数えている）")
    for t, level, rise in outside[:12]:
        print(f"            {t:7.2f}s  {level:6.1f} dBFS（局所 +{rise:.1f} dB）")

    # 効果音 1 本ずつの立ち上がり（鳴る前 1.7 秒の中央値から、鳴り始め 0.8 秒の最大へ）
    if args.mix:
        print("  効果音ごと（鳴る前からの立ち上がり）")
        for stem in spec.get("stems", []):
            if stem.get("role") != "hit":
                continue
            t0 = float(stem.get("start") or 0.0)
            i0 = int(max(0.0, t0) / HOP)
            i1 = min(len(db), i0 + int(0.8 / HOP))
            # 手前は「鳴る直前の 0.5 秒」。2 秒取ると台詞の尾を拾い、間の中の効果音が
            # 台詞より静かに見える（間の長さと効果音の長さが同じ意味を持つ作品では誤読になる）。
            p0, p1 = max(0, i0 - int(0.5 / HOP)), max(1, i0 - int(0.05 / HOP))
            if i1 <= i0 or p1 <= p0:
                continue
            peak = float(db[i0:i1].max())
            pre = float(np.median(db[p0:p1]))
            print(f"            {t0:7.2f}s  {peak:6.1f} dBFS / 手前 {pre:6.1f} → "
                  f"+{peak - pre:5.1f} dB  {'合格' if peak - pre >= BURST_DB else '未達'}"
                  f"  {stem.get('file','')}")
    print(f"  大きな音の中央値 {np.median(db[~sil]):6.1f} dBFS / 小さい方の 10% "
          f"{np.percentile(db, 10):6.1f} dBFS")


if __name__ == "__main__":
    main()
