"""文末の句読点を替えると、語尾の抑揚が変わるか。

    PYTHONPATH=. $PY projects/longform/acting-punctuation/run.py

同じ 1 行の末尾だけを「。」「？」「！」と、句点なしに替えて焼く
（4 通り × seed 5 = 20 本）。Spec は `acting-subtext/llm-specs.json` の none
（neutral・0.5・controlled）で共通、`prosody.intonation` も neutral のまま。
＝抑揚の指定ではなく、**台詞の字面だけ**を振る。
出す先は `projects/longform/assets/acting-punctuation/voice/`。
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

OUT = "projects/longform/assets/acting-punctuation/voice"
config.ALPHA, config.BETA = 0.35, 0.7
os.makedirs(OUT, exist_ok=True)

LINES = {
    "period": "明日、また来るね。",
    "question": "明日、また来るね？",
    "exclaim": "明日、また来るね！",
    "none": "明日、また来るね",
}

base = json.load(open("projects/longform/acting-subtext/llm-specs.json"))["none"]["spec"]
vp = load_voice_profile(character_path("mashiro"))
prov = TsukasaProvider()

for key, line in LINES.items():
    for seed in range(1, 6):
        path = os.path.join(OUT, f"pn-{key}-s{seed}.wav")
        if os.path.exists(path):
            continue
        req = GenerationRequest(
            asset_type="voice", spec=base, seed=seed, voice_profile=vp, dialogue=line,
        )
        audio = prov.generate(req)
        sf.write(path, np.asarray(audio.wav, dtype=np.float32), config.SAMPLE_RATE)
        print("wrote", path, flush=True)
print("done")
