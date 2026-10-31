#!/usr/bin/env python
"""配布用の mp3 を作る（耳の代わりの門番・その 3）。

`check_loudness.py` は測るだけ。ここでは**直線のゲインだけ**を掛けて、
配布の目安に寄せてから mp3 を書き出す。compress も limiter も掛けない
（長い無音と大きな山が混ざる素材では、動くゲインが呼吸のように聴こえる）。

掛け方は 1 本 1 値:

    gain = min(−16 − I,  −1.0 − TP)      ← mp3 を測り直して 1 回だけ直す

−16 LUFS へ寄せたいが、**トゥルーピークが −1.0 dBTP を超えるならそこで止める**。
だから音量の側が届かないことがある（それは記録に残す）。mp3 は wav より
0.2〜0.3 dB 低く、ピークは高く出るので、**測り直してから決める**。

  PYTHONPATH=. <venv> .../deliver.py <台本の wav> <書き先の mp3> [--gain G]

`--gain` を渡すと計算せずにその値で書く（**全作品へ同じ値を掛ける**ときや、
対で聴く見本を同じ高さにそろえるとき）。元の wav（マスター）は触らない。
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys

TARGET_I = -16.0
TARGET_TP = -1.0


def measure(path: str) -> dict[str, float]:
    err = subprocess.run(
        ["ffmpeg", "-nostats", "-i", path, "-af", "loudnorm=print_format=json",
         "-f", "null", "-"],
        capture_output=True, text=True,
    ).stderr
    blob = err[err.index("{"):err.rindex("}") + 1]
    d = json.loads(blob)
    return {"i": float(d["input_i"]), "tp": float(d["input_tp"]), "lra": float(d["input_lra"])}


def encode(src: str, dst: str, gain: float) -> None:
    subprocess.run(
        ["ffmpeg", "-y", "-nostats", "-i", src,
         "-af", f"volume={gain:.2f}dB",
         # **チャンネル数はマスターのまま**。`-ac 2` を付けると、モノラルの音を
         # ステレオへ上げるとき ffmpeg が 0.707 倍ずつ配るので、−3 dB 静かになる。
         "-ar", "44100", "-c:a", "libmp3lame", "-b:a", "192k", dst],
        check=True, capture_output=True,
    )


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("dst")
    ap.add_argument("--gain", type=float, default=None)
    args = ap.parse_args()

    before = measure(args.src)
    gain = args.gain if args.gain is not None else min(
        TARGET_I - before["i"], TARGET_TP - before["tp"])
    encode(args.src, args.dst, gain)
    after = measure(args.dst)
    if args.gain is None:
        # mp3 は wav より低く出て、ピークは高く出る。1 回だけ直す。
        gain += min(TARGET_I - after["i"], TARGET_TP - after["tp"])
        encode(args.src, args.dst, gain)
        after = measure(args.dst)
    if abs(after["i"] - TARGET_I) <= 0.5:
        reached = "届いた"
    elif args.gain is not None:
        reached = "届かず（`--gain` の値で書いた）"
    else:
        reached = "届かず（ピークで止めた）"
    print(f"{args.src.rsplit('/', 1)[-1]}")
    print(f"  元   I {before['i']:.2f} LUFS  TP {before['tp']:.2f} dBTP  LRA {before['lra']:.2f}")
    print(f"  ゲイン {gain:+.2f} dB（直線・圧縮なし）")
    print(f"  mp3  I {after['i']:.2f} LUFS  TP {after['tp']:.2f} dBTP  LRA {after['lra']:.2f}"
          f"  → −16 LUFS へ {reached}")


if __name__ == "__main__":
    main()
