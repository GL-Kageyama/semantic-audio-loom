#!/usr/bin/env python
"""仕上げた 1 本の音量を、配布の目安と突き合わせる（耳の代わりの門番・その 2）。

ピークの正規化（0.95）は「いちばん大きい瞬間」をそろえるだけで、**体感の音量は
そろわない**。ここでは ffmpeg の loudnorm で測った値を出す。

  PYTHONPATH=. <venv> .../check_loudness.py <wav|mp3> [...]

目安（配布先の慣習。この工房の裁定ではない）:
- 統合の音量 −16 LUFS（ポッドキャストの目安）± 1.0
- トゥルーピーク −1.0 dBTP 以下（可逆圧縮で 0 dBFS を超えないため）
- 音量の幅 LRA は 12 LU 以下（長い無音と大きな山が混ざりすぎていないか）
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys

TARGET_I = -16.0
TOL_I = 1.0
MAX_TP = -1.0
MAX_LRA = 12.0


def measure(path: str) -> dict[str, float]:
    out = subprocess.run(
        ["ffmpeg", "-nostats", "-i", path, "-af", "loudnorm=print_format=json",
         "-f", "null", "-"],
        capture_output=True, text=True,
    ).stderr
    blob = out[out.index("{"):out.rindex("}") + 1]
    d = json.loads(blob)
    return {"i": float(d["input_i"]), "tp": float(d["input_tp"]), "lra": float(d["input_lra"])}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    args = ap.parse_args()
    if not shutil.which("ffmpeg"):
        sys.exit("ffmpeg が無い")
    print(f"{'ファイル':52s} {'I LUFS':>8s} {'TP dBTP':>8s} {'LRA LU':>7s}  判定")
    for p in args.files:
        m = measure(p)
        bad = []
        if abs(m["i"] - TARGET_I) > TOL_I:
            bad.append("音量")
        if m["tp"] > MAX_TP:
            bad.append("ピーク")
        if m["lra"] > MAX_LRA:
            bad.append("幅")
        verdict = "合格" if not bad else "未達（" + "・".join(bad) + "）"
        print(f"{p[-52:]:52s} {m['i']:8.2f} {m['tp']:8.2f} {m['lra']:7.2f}  {verdict}")


if __name__ == "__main__":
    main()
