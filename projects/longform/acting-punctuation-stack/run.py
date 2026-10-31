"""文末の記号と感情は、足し算になるか。

    PYTHONPATH=. $PY projects/longform/acting-punctuation-stack/run.py

台詞の最後（`。` / `！`）× 感情（neutral / joy）の 2 × 2 を seed 5 で焼く
（4 通り × 5 = 20 本）。ほかの欄は `acting-subtext/llm-specs.json` の none と同じ。
出す先は `projects/longform/assets/acting-punctuation-stack/voice/`。
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

OUT = "projects/longform/assets/acting-punctuation-stack/voice"
config.ALPHA, config.BETA = 0.35, 0.7
os.makedirs(OUT, exist_ok=True)

LINES = {"period": "明日、また来るね。", "exclaim": "明日、また来るね！"}

base = json.load(open("projects/longform/acting-subtext/llm-specs.json"))["none"]["spec"]
vp = load_voice_profile(character_path("mashiro"))
prov = TsukasaProvider()

for emotion in ("neutral", "joy"):
    for mark, line in LINES.items():
        spec = copy.deepcopy(base)
        spec.setdefault("emotion", {})["primary"] = emotion
        for seed in range(1, 6):
            path = os.path.join(OUT, f"ps-{emotion}-{mark}-s{seed}.wav")
            if os.path.exists(path):
                continue
            req = GenerationRequest(
                asset_type="voice", spec=spec, seed=seed, voice_profile=vp,
                dialogue=line,
            )
            audio = prov.generate(req)
            sf.write(path, np.asarray(audio.wav, dtype=np.float32), config.SAMPLE_RATE)
            print("wrote", path, flush=True)
print("done")
