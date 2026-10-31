"""`llm-specs.json` の 5 つの Spec を、seed 1〜5 で焼く（LLM は呼ばない）。

    PYTHONPATH=. $PY projects/longform/acting-subtext/run_llm_specs.py

subtext を LLM に解決させた Spec（`--resolve llm` の出力）を固定してから焼くので、
「LLM の出力が揺れる」ぶんと「声が揺れる」ぶんを分けて測れる。
出す先は `projects/longform/assets/acting-subtext-llm/voice/`。
"""
import json
import os
import sys

sys.path.insert(0, os.getcwd())

import numpy as np
import soundfile as sf

from semantic_audio_loom import config
from semantic_audio_loom.providers.tsukasa import TsukasaProvider, _spec_prompt, _subject
from semantic_audio_loom.skills.character_voice import character_path, load_voice_profile
from semantic_audio_loom.types import GenerationRequest

HERE = "projects/longform/acting-subtext"
OUT = "projects/longform/assets/acting-subtext-llm/voice"
LINE = "明日、また来るね。"

config.ALPHA, config.BETA = 0.35, 0.7
os.makedirs(OUT, exist_ok=True)

specs = json.load(open(os.path.join(HERE, "llm-specs.json")))
vp = load_voice_profile(character_path("mashiro"))
prov = TsukasaProvider()

lines = []
for key, entry in specs.items():
    prompt = _spec_prompt(_subject(vp), entry["spec"])
    lines.append(f"{key}\t{prompt}\n")
    for seed in range(1, 6):
        path = os.path.join(OUT, f"stl-{key}-s{seed}.wav")
        if os.path.exists(path):
            continue
        req = GenerationRequest(
            asset_type="voice", spec=entry["spec"], seed=seed,
            voice_profile=vp, dialogue=LINE,
        )
        audio = prov.generate(req)
        wav = np.asarray(audio.wav, dtype=np.float32)
        sf.write(path, wav, config.SAMPLE_RATE)
        print("wrote", path, flush=True)

with open(os.path.join(HERE, "llm-prompts.tsv"), "w") as f:
    f.writelines(lines)
print("done")
