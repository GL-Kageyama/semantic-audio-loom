#!/usr/bin/env python
"""CLI: 台詞 1 本を演技の言葉で測る。

  bin/act_probe.py projects/longform/assets/acting-matrix/voice/*.wav
  bin/act_probe.py --json projects/longform/assets/acting-matrix/voice/em-joy-s1.wav
  bin/act_probe.py --tsv projects/longform/assets/acting-matrix/voice/*.wav \
    > projects/longform/experiments/basics/acting-matrix/matrix.tsv

良し悪しは判定しない。感情ごとに「何が動いたか」を数で言えるようにする計器。
指標の定義は semantic_audio_loom/skills/act_probe.py の冒頭に書いてある。
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from semantic_audio_loom import i18n
from semantic_audio_loom.skills import act_probe


def _fmt(value, unit: str = "") -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:g}{unit}"
    return f"{value}{unit}"


def _line(t, e: dict) -> list[str]:
    return [
        "  " + t("act_probe", "pitch",
                 "声の高さ {f0} Hz / 抑揚 {rng} 半音 / 語尾 {end} 半音/秒",
                 f0=_fmt(e["f0_median_hz"]), rng=_fmt(e["f0_range_st"]),
                 end=_fmt(e["f0_end_st_s"])),
        "  " + t("act_probe", "time",
                 "速さ {rate} 拍/秒 / 間 {pause}% / 有声 {voiced}%",
                 rate=_fmt(e["rate_mora_s"]),
                 pause=_fmt(round(e["pause_ratio"] * 100, 1) if e["pause_ratio"] is not None else None),
                 voiced=_fmt(round(e["voiced_fraction"] * 100, 1) if e["voiced_fraction"] is not None else None)),
        "  " + t("act_probe", "energy",
                 "張り {med} dB（幅 {rng}） / 立ち上がり {atk} ms / 長さ {dur} 秒",
                 med=_fmt(e["energy_median_db"]), rng=_fmt(e["energy_range_db"]),
                 atk=_fmt(e["attack_ms"]), dur=_fmt(e["duration"])),
    ]


def main() -> None:
    lang, loc, t = i18n.translator()
    p = argparse.ArgumentParser(
        description=t("act_probe", "description", "台詞 1 本を演技の言葉で測る。"))
    i18n.add_lang_argument(p)
    p.add_argument("wav", nargs="+")
    p.add_argument("--json", action="store_true", help=t("act_probe", "help_json", "JSON で出す"))
    p.add_argument("--tsv", action="store_true", help=t("act_probe", "help_tsv", "TSV で出す（表へ貼る）"))
    args = p.parse_args()

    results = []
    for path in args.wav:
        try:
            entry = act_probe.measure(path)
        except Exception as exc:
            print(f"NG {path}: {exc}", file=sys.stderr)
            continue
        results.append(entry)
        if not args.json and not args.tsv:
            print(path)
            print("\n".join(_line(t, entry)))

    if args.tsv:
        cols = act_probe.COLUMNS
        print("\t".join(cols))
        for e in results:
            print("\t".join("" if e.get(c) is None else str(e.get(c)) for c in cols))
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
