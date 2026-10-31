#!/usr/bin/env python
"""未達の 2 本に、圧縮（loudnorm の 2 パス）を掛けたらどうなるかを測って並べる。

`deliver.py` は**直線のゲインだけ**で、ピークに当たった素材は −16 LUFS へ届かない。
ここでは同じ素材へ `loudnorm`（1 パス目で測り、2 パス目で当てる＝動く圧縮）を掛けて、
**届くか・何を失うか**を数で出す。mp3 は試作として同じ場所に置く（`examples/` には
足さない——掛け方が裁定されていない）。

  PYTHONPATH=. <venv>/bin/python projects/longform/experiments/analysis/loudness-trial/make_trial.py

結果は `result.tsv`。圧縮の前後で**音量（I）・ピーク（TP）・幅（LRA）・波高率**を測る。
"""
from __future__ import annotations

import json
import os
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))


def _lf_root(d=HERE):
    """projects/longform の根まで上へ辿る（REPORT.md と assets のある所）。"""
    while not os.path.exists(os.path.join(d, "REPORT.md")):
        d = os.path.dirname(d)
    return d

ROOT = _lf_root()          # projects/longform
ASSETS = os.path.join(ROOT, "assets")
SOURCES = ("explainer", "drama-scene-mark")
TARGET = "I=-16:TP=-1.0:LRA=11"


def probe(path: str) -> dict:
    """loudnorm の 1 パス目の値をそのまま使う（測りと当てを同じ物差しに）。"""
    err = subprocess.run(
        ["ffmpeg", "-nostats", "-i", path, "-af", f"loudnorm={TARGET}:print_format=json",
         "-f", "null", "-"], capture_output=True, text=True).stderr
    d = json.loads(err[err.index("{"):err.rindex("}") + 1])
    return {k: float(v) for k, v in d.items()
            if k in ("input_i", "input_tp", "input_lra", "input_thresh", "target_offset")}


def crest(path: str) -> tuple[float, float]:
    """ピークと RMS（dB）。差が波高率。astats の Summary から取る。"""
    err = subprocess.run(
        ["ffmpeg", "-nostats", "-i", path, "-af", "astats=metadata=1:measure_overall=Peak_level+RMS_level",
         "-f", "null", "-"], capture_output=True, text=True).stderr
    peak = rms = float("nan")
    for line in err.splitlines():
        if "Peak level dB:" in line:          # astats は行頭に "[Parsed_astats_0 @ ...]" を付ける
            peak = float(line.rsplit("Peak level dB:", 1)[1])
        elif "RMS level dB:" in line:
            rms = float(line.rsplit("RMS level dB:", 1)[1])
    return peak, rms


def main() -> None:
    rows = ["work\tstage\tI_LUFS\tTP_dBTP\tLRA_LU\tpeak_db\trms_db\tcrest_db"]
    for work in SOURCES:
        src = os.path.join(ASSETS, work, "renders", f"{work}.wav")
        dst = os.path.join(HERE, f"{work}-compressed.mp3")
        m = probe(src)
        p0, r0 = crest(src)
        rows.append(f"{work}\tbefore\t{m['input_i']:.2f}\t{m['input_tp']:.2f}\t"
                    f"{m['input_lra']:.2f}\t{p0:.1f}\t{r0:.1f}\t{p0 - r0:.1f}")
        af = (f"loudnorm={TARGET}:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
              f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
              f"offset={m['target_offset']}:linear=false")
        subprocess.run(["ffmpeg", "-y", "-nostats", "-i", src, "-af", af, "-ar", "44100",
                        "-c:a", "libmp3lame", "-b:a", "192k", dst],
                       check=True, capture_output=True)
        m2 = probe(dst)
        p1, r1 = crest(dst)
        rows.append(f"{work}\tafter\t{m2['input_i']:.2f}\t{m2['input_tp']:.2f}\t"
                    f"{m2['input_lra']:.2f}\t{p1:.1f}\t{r1:.1f}\t{p1 - r1:.1f}")
        print(rows[-2]); print(rows[-1])
    with open(os.path.join(HERE, "result.tsv"), "w", encoding="utf-8") as f:
        f.write("\n".join(rows) + "\n")


if __name__ == "__main__":
    main()
