"""長い行の効きが縮んだのは、長さのせいか、途中の句点のせいか。

    PYTHONPATH=. $PY projects/longform/acting-punctuation-long/run_comma.py

`run.py` の 24 文字の行は途中に句点が 1 つある（「最初に会ったとき。画面の…」）。
途中を読点に替えた同じ 24 文字の行で、末尾だけを `。` / `！` に振る
（2 通り × seed 5 = 10 本）。長さをそろえたまま、途中の句点だけを外した対照。
出す先は `projects/longform/assets/acting-punctuation-long/voice/`（`plc-` の札）。
"""
import json
import os
import sys

sys.path.insert(0, os.getcwd())

import numpy as np
import soundfile as sf

from semantic_audio_loom import config
from semantic_audio_loom.providers.tsukasa import TsukasaProvider
from semantic_audio_loom.skills.character_voice import character_path, load_voice_profile
from semantic_audio_loom.types import GenerationRequest

OUT = "projects/longform/assets/acting-punctuation-long/voice"
config.ALPHA, config.BETA = 0.35, 0.7
os.makedirs(OUT, exist_ok=True)

STEM = "最初に会ったとき、画面の向こうで、虹が揺れてた"
LINES = {
    "period": STEM + "。",
    "exclaim": STEM + "！",
}

base = json.load(open("projects/longform/acting-subtext/llm-specs.json"))["none"]["spec"]
vp = load_voice_profile(character_path("mashiro"))
prov = TsukasaProvider()

for key, line in LINES.items():
    for seed in range(1, 6):
        path = os.path.join(OUT, f"plc-{key}-s{seed}.wav")
        if os.path.exists(path):
            continue
        req = GenerationRequest(
            asset_type="voice", spec=base, seed=seed, voice_profile=vp, dialogue=line,
        )
        audio = prov.generate(req)
        sf.write(path, np.asarray(audio.wav, dtype=np.float32), config.SAMPLE_RATE)
        print("wrote", path, flush=True)
print("done")
