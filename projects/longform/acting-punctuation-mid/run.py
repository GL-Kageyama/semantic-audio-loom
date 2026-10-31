"""文末の記号の効きは、行の長さでどこまで縮むか（真ん中の長さを足す）。

    PYTHONPATH=. $PY projects/longform/acting-punctuation-mid/run.py

`acting-punctuation/`（9 文字）と `acting-punctuation-long/`（24 文字）の
あいだを埋める。同じ長い行から頭の 1 節を落とした 14 文字の行で、
末尾だけを `。` / `！` に替える（2 通り × seed 5 = 10 本）。
Spec は `acting-subtext/llm-specs.json` の none（neutral・0.5・controlled）で共通。
出す先は `projects/longform/assets/acting-punctuation-mid/voice/`。
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

OUT = "projects/longform/assets/acting-punctuation-mid/voice"
config.ALPHA, config.BETA = 0.35, 0.7
os.makedirs(OUT, exist_ok=True)

STEM = "画面の向こうで、虹が揺れてた"
LINES = {
    "period": STEM + "。",
    "exclaim": STEM + "！",
}

base = json.load(open("projects/longform/acting-subtext/llm-specs.json"))["none"]["spec"]
vp = load_voice_profile(character_path("mashiro"))
prov = TsukasaProvider()

for key, line in LINES.items():
    for seed in range(1, 6):
        path = os.path.join(OUT, f"pm-{key}-s{seed}.wav")
        if os.path.exists(path):
            continue
        req = GenerationRequest(
            asset_type="voice", spec=base, seed=seed, voice_profile=vp, dialogue=line,
        )
        audio = prov.generate(req)
        sf.write(path, np.asarray(audio.wav, dtype=np.float32), config.SAMPLE_RATE)
        print("wrote", path, flush=True)
print("done")
