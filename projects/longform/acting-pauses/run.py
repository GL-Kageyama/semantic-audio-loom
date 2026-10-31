"""読点を足すと、間になるか（`prosody.pauses` は散文に入らないので、その代わり）。

    PYTHONPATH=. $PY projects/longform/acting-pauses/run.py

台詞の「明日」のあとに読点を 0 / 1 / 2 個置いて焼く（3 通り × seed 5 = 15 本）。
`normalize_ellipsis` は文中の「…」を「、」にするので、2 個の読点は
「……（ためらい）」を書いたときに出る形でもある。
出す先は `projects/longform/assets/acting-pauses/voice/`。
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

OUT = "projects/longform/assets/acting-pauses/voice"
config.ALPHA, config.BETA = 0.35, 0.7
os.makedirs(OUT, exist_ok=True)

LINES = {
    "c1": "明日、また来るね。",
    "c2": "明日、、また来るね。",
    "c3": "明日、、、また来るね。",
}

base = json.load(open("projects/longform/acting-subtext/llm-specs.json"))["none"]["spec"]
vp = load_voice_profile(character_path("mashiro"))
prov = TsukasaProvider()

for key, line in LINES.items():
    for seed in range(1, 6):
        path = os.path.join(OUT, f"pz-{key}-s{seed}.wav")
        if os.path.exists(path):
            continue
        req = GenerationRequest(
            asset_type="voice", spec=base, seed=seed, voice_profile=vp, dialogue=line,
        )
        audio = prov.generate(req)
        sf.write(path, np.asarray(audio.wav, dtype=np.float32), config.SAMPLE_RATE)
        print("wrote", path, flush=True)
print("done")
