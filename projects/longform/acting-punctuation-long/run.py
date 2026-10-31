"""文末の記号は、長い台詞でも効くか。

    PYTHONPATH=. $PY projects/longform/acting-punctuation-long/run.py

`acting-punctuation/` は 9 文字の一言で測った。ここでは芝居の長い行
（`acting-longline/` と同じ 24 文字・句読点 2 つの行）の末尾だけを
「。」「？」「！」「？！」に替える（4 通り × seed 5 = 20 本）。
Spec は `acting-subtext/llm-specs.json` の none（neutral・0.5・controlled）で共通。
出す先は `projects/longform/assets/acting-punctuation-long/voice/`。
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

STEM = "最初に会ったとき。画面の向こうで、虹が揺れてた"
LINES = {
    "period": STEM + "。",
    "question": STEM + "？",
    "exclaim": STEM + "！",
    "double": STEM + "？！",
}

base = json.load(open("projects/longform/acting-subtext/llm-specs.json"))["none"]["spec"]
vp = load_voice_profile(character_path("mashiro"))
prov = TsukasaProvider()

for key, line in LINES.items():
    for seed in range(1, 6):
        path = os.path.join(OUT, f"pl-{key}-s{seed}.wav")
        if os.path.exists(path):
            continue
        req = GenerationRequest(
            asset_type="voice", spec=base, seed=seed, voice_profile=vp, dialogue=line,
        )
        audio = prov.generate(req)
        sf.write(path, np.asarray(audio.wav, dtype=np.float32), config.SAMPLE_RATE)
        print("wrote", path, flush=True)
print("done")
