"""同じ語を、かな・カナ・漢字で書くと声が変わるか（＋語のあとに読点）。

    PYTHONPATH=. $PY projects/longform/acting-notation/run.py

「明日、また来るね。」の「また」だけを書き換える（4 通り × seed 5 = 20 本・beta 0.7）。
Spec は `acting-subtext/llm-specs.json` の none と同じ。
出す先は `projects/longform/assets/acting-notation/voice/`。
"""
import copy
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

OUT = "projects/longform/assets/acting-notation/voice"
config.ALPHA, config.BETA = 0.35, 0.7
os.makedirs(OUT, exist_ok=True)

LINES = {
    "hira": "明日、また来るね。",
    "kata": "明日、マタ来るね。",
    "kanji": "明日、又来るね。",
    "comma": "明日、また、来るね。",
}

base = json.load(open("projects/longform/acting-subtext/llm-specs.json"))["none"]["spec"]
vp = load_voice_profile(character_path("mashiro"))
prov = TsukasaProvider()

for key, line in LINES.items():
    for seed in range(1, 6):
        path = os.path.join(OUT, f"nt-{key}-s{seed}.wav")
        if os.path.exists(path):
            continue
        req = GenerationRequest(
            asset_type="voice", spec=copy.deepcopy(base), seed=seed,
            voice_profile=vp, dialogue=line,
        )
        audio = prov.generate(req)
        sf.write(path, np.asarray(audio.wav, dtype=np.float32), config.SAMPLE_RATE)
        print("wrote", path, flush=True)
print("done")
