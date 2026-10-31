#!/usr/bin/env python
"""強度の真ん中の文言を差し替えて、同じ build_voice の道で作る。

  PYTHONPATH=. <venv> .../mod_phrase_build.py --dir <作品の dir> [--phrase "..."] [--band 0.70]

原本は触らない。tsukasa._INTENSITY_PHRASES をプロセスの中だけで差し替える。
_intensity_phrase() は呼ぶたびにモジュールの表を読むので、差し替えは効く。

--phrase を渡さなければ、既定の表のまま（対照を同じ道で作るとき）。
--band は文言を置く帯の上端（0.70 なら 0.40〜0.70。0.90 なら strong の段）。
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))          # projects/longform/acting
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))  # リポジトリの根
sys.path.insert(0, REPO)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--phrase", default="", help="差し込む文言（空なら既定のまま）")
    ap.add_argument("--band", type=float, default=0.70, help="文言を置く帯の上端")
    args, rest = ap.parse_known_args()

    from semantic_audio_loom.providers import tsukasa

    if args.phrase:
        band = args.band
        table = list(tsukasa._INTENSITY_PHRASES)
        # 上端が band の段を、同じ上端のまま文言だけ差し替える（無ければ足す）。
        table = [(upper, args.phrase if abs(upper - band) < 1e-9 else text)
                 for upper, text in table]
        tsukasa._INTENSITY_PHRASES = tuple(table)

    path = os.path.join(REPO, "projects", "longform", "explainer", "build_voice.py")
    spec = importlib.util.spec_from_file_location("longform_build_voice", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    sys.argv = ["build_voice.py", "--dir", args.dir] + rest
    mod.main()


if __name__ == "__main__":
    main()

