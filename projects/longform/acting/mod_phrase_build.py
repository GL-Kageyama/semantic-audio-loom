#!/usr/bin/env python
"""強度の真ん中の文言を差し替えて、同じ build_voice の道で作る。

  PYTHONPATH=. <venv> projects/longform/acting/mod_phrase_build.py --dir projects/longform/acting-mod-phrase

原本は触らない。tsukasa._INTENSITY_PHRASES をプロセスの中だけで差し替える。
_intensity_phrase() は呼ぶたびにモジュールの表を読むので、差し替えは効く。
"""
from __future__ import annotations

import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))          # projects/longform/acting
REPO = os.path.dirname(os.path.dirname(os.path.dirname(HERE)))  # リポジトリの根
sys.path.insert(0, REPO)

from semantic_audio_loom.providers import tsukasa  # noqa: E402

# 0.40〜0.70 の帯（既定は空文字）に文言を置く。ほかの段は既定のまま。
tsukasa._INTENSITY_PHRASES = (
    (0.40, "the feeling is faint, barely showing"),
    (0.70, "the feeling is moderately strong"),
    (0.90, "the feeling is strong, close to the surface"),
    (1.01, "the feeling is overwhelming, at its limit"),
)

path = os.path.join(REPO, "projects", "longform", "explainer", "build_voice.py")
spec = importlib.util.spec_from_file_location("longform_build_voice", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

sys.argv = ["build_voice.py"] + sys.argv[1:]
mod.main()
