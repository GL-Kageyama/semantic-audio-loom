"""文末の記号の効きが、別の人物・別の行でも出るか。

    PYTHONPATH=. $PY projects/longform/experiments/punctuation/acting-punctuation/run_second_speaker.py

ニジの声で「今、行くよ。」と「今、行くよ！」を seed 5 ずつ（10 本・beta 0.7）。
Spec は `experiments/subtext/acting-subtext/llm-specs.json` の none と同じ。
出す先は `projects/longform/assets/acting-punctuation-niji/voice/`。
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

OUT = "projects/longform/assets/acting-punctuation-niji/voice"
config.ALPHA, config.BETA = 0.35, 0.7
os.makedirs(OUT, exist_ok=True)

LINES = {"period": "今、行くよ。", "exclaim": "今、行くよ！"}

base = json.load(open("projects/longform/experiments/subtext/acting-subtext/llm-specs.json"))["none"]["spec"]
vp = load_voice_profile(character_path("niji"))
prov = TsukasaProvider()

for mark, line in LINES.items():
    for seed in range(1, 6):
        path = os.path.join(OUT, f"pnj-{mark}-s{seed}.wav")
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
