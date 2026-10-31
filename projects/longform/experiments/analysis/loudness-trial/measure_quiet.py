#!/usr/bin/env python
"""圧縮が「どこをどれだけ持ち上げたか」を、入力の高さごとに測る（伝達の表）。

波高率（ピーク − RMS）は 1 つの数でしかない。ここでは 100 ms ごとの
momentary loudness（M）を前後のファイルから**同じ時刻で**取り、**圧縮前の高さで
8 帯に分けて**、それぞれ何 dB 上がったかを出す。小さい音ほど大きく上がっていれば、
山と谷の差が縮んでいる（＝情報量が減っている）。

  PYTHONPATH=. <venv>/bin/python projects/longform/experiments/analysis/loudness-trial/measure_quiet.py

- 時刻は 0.1 秒に丸めて突き合わせる（mp3 は頭に 25 ms の遅れが入るので、
  並び順ではなく時刻で対にする）。
- 圧縮前の M が −50 dB 以下のフレームは「間」。圧縮しても間は上がらないので外す。
- `LRA` は ebur128 の loudness range（門は 12 LU 以下）。
"""
from __future__ import annotations

import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))


def _lf_root(d=HERE):
    """projects/longform の根まで上へ辿る（REPORT.md と assets のある所）。"""
    while not os.path.exists(os.path.join(d, "REPORT.md")):
        d = os.path.dirname(d)
    return d

ROOT = _lf_root()
ASSETS = os.path.join(ROOT, "assets")
PAIRS = (
    ("explainer", os.path.join(ASSETS, "explainer", "renders", "explainer.wav"),
     os.path.join(HERE, "explainer-compressed.mp3")),
    ("drama-scene-mark", os.path.join(ASSETS, "drama-scene-mark", "renders", "drama-scene-mark.wav"),
     os.path.join(HERE, "drama-scene-mark-compressed.mp3")),
)
FRAME = re.compile(r"t:\s*([0-9.]+).*?M:\s*(-?[0-9.]+)")
SILENCE_REF = -50.0   # 圧縮前の M がこれ以下のフレームは「間」。対象から外す
BANDS = 8


def frames(path: str) -> dict[float, float]:
    """時刻（0.1 秒に丸め）→ M。framelog=verbose は verbose 段なので loglevel が要る。"""
    err = subprocess.run(
        ["ffmpeg", "-nostats", "-loglevel", "verbose", "-i", path,
         "-af", "ebur128=framelog=verbose", "-f", "null", "-"],
        capture_output=True, text=True).stderr
    return {round(float(m.group(1)), 1): float(m.group(2)) for m in FRAME.finditer(err)}


def loudnorm(path: str) -> dict:
    err = subprocess.run(
        ["ffmpeg", "-nostats", "-i", path, "-af", "loudnorm=print_format=json",
         "-f", "null", "-"], capture_output=True, text=True).stderr
    d = json.loads(err[err.index("{"):err.rindex("}") + 1])
    return {k: float(d[k]) for k in ("input_i", "input_lra", "input_tp")}


def main() -> None:
    print("work\tI_before\tI_after\tLRA_before\tLRA_after")
    for work, src, cmp_ in PAIRS:
        a, b = loudnorm(src), loudnorm(cmp_)
        print(f"{work}\t{a['input_i']:.2f}\t{b['input_i']:.2f}\t"
              f"{a['input_lra']:.2f}\t{b['input_lra']:.2f}")
    print()
    print("work\tband_lo\tband_hi\tn\traise_db")
    for work, src, cmp_ in PAIRS:
        fa, fb = frames(src), frames(cmp_)
        keys = [k for k in sorted(set(fa) & set(fb)) if fa[k] > SILENCE_REF]
        lv = [fa[k] for k in keys]
        lo, hi = min(lv), max(lv)
        step = (hi - lo) / BANDS
        for i in range(BANDS):
            band = [k for k in keys if lo + i * step <= fa[k]
                    and (fa[k] < lo + (i + 1) * step or i == BANDS - 1)]
            if not band:
                continue
            rise = sum(fb[k] - fa[k] for k in band) / len(band)
            print(f"{work}\t{lo + i * step:.1f}\t{lo + (i + 1) * step:.1f}\t"
                  f"{len(band)}\t{rise:+.1f}")


if __name__ == "__main__":
    main()
