#!/usr/bin/env python
"""CLI: 生成した音を測る（耳の代わりの診断器）。

  bin/probe.py examples/sound-samples/*.wav
  bin/probe.py projects/demo/assets/sound/bgm.wav --json

良し悪しは判定しない。無音・クリップ・高域の完全な欠落・先頭の段差など、
機械的に明らかな欠陥だけを「注意」として出す。
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from semantic_audio_loom import i18n
from semantic_audio_loom.skills import probe


def _line(t, e: dict) -> list[str]:
    bands = e["bands_db"]
    out = [
        "  " + t("probe", "fmt", "形式 {khz} kHz / {ch} ch / {bits} bit / {dur} 秒",
                 khz=f"{e['sample_rate'] / 1000:g}", ch=e["channels"],
                 bits=e["bits"], dur=f"{e['duration']:g}"),
        "  " + t("probe", "level",
                 "レベル ピーク {peak} / RMS {rms} dBFS / クレスト {crest} dB / DC {dc}",
                 peak=e["peak"], rms=e["rms_db"], crest=e["crest_db"], dc=e["dc"]),
        "  " + t("probe", "silence", "無音率 {pct}% / クリップ {clip}",
                 pct=round(e["silent_fraction"] * 100, 1), clip=e["clipped"]),
        "  " + t("probe", "bands",
                 "帯域 低 {low} dB / 中 {mid} dB / 高 {high} dB",
                 low=bands["low"], mid=bands["mid"], high=bands["high"]),
        "  " + t("probe", "centroid", "重心 {hz} Hz / 平坦度 {flat}",
                 hz=e["centroid_hz"], flat=e["flatness"]),
    ]
    if e["flags"]:
        for name, values in e["flags"]:
            default = {
                "silent": "ほぼ無音（RMS {rms_db} dBFS）",
                "clipped": "クリップ {count} サンプル",
                "bass_heavy": "低域に寄っている（低が中より {diff_db} dB 大きい）",
                "no_highs": "2kHz 以上がほぼ無い（{level_db} dB）",
                "head_step": "先頭が 0 から始まっていない（{value}）",
            }[name]
            out.append("  " + t("probe", f"flag_{name}", default, **values))
    else:
        out.append("  " + t("probe", "ok", "機械的な欠陥は見つからない"))
    return out


def main() -> None:
    lang, loc, t = i18n.translator()
    p = argparse.ArgumentParser(description=t("probe", "description", "生成した音を測る。"))
    i18n.add_lang_argument(p)
    p.add_argument("wav", nargs="+")
    p.add_argument("--json", action="store_true", help=t("probe", "help_json", "JSON で出す"))
    args = p.parse_args()

    results = []
    for path in args.wav:
        try:
            entry = probe.measure(path)
        except Exception as exc:
            print(f"NG {path}: {exc}", file=sys.stderr)
            continue
        results.append(entry)
        if not args.json:
            print(path)
            print("\n".join(_line(t, entry)))
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
