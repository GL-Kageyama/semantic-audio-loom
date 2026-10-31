"""`明日、、また来るね` で、後ろの節が読まれているかを長さで見る。

    PYTHONPATH=. $PY projects/longform/acting-punctuation-ellipsis-mid/run_trunc.py

途中の `…` は `、` になるので、字面は `明日、、また来るね`。この 5 本は
`なし`（`明日、また来るね`・2.918 秒）より 0.85 秒短い。短いのが「速く読んだ」
のか「後ろを読んでいない」のかを、頭だけの行（`明日、` / `明日、、`）の長さと
比べて見る。seed 1・2 の 2 本ずつ。
出す先は `projects/longform/assets/acting-punctuation-ellipsis-mid/voice/`。
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

OUT = "projects/longform/assets/acting-punctuation-ellipsis-mid/voice"
config.ALPHA, config.BETA = 0.35, 0.7
os.makedirs(OUT, exist_ok=True)

LINES = {"head": "明日、", "head2": "明日、、"}

base = json.load(open("projects/longform/acting-subtext/llm-specs.json"))["none"]["spec"]
vp = load_voice_profile(character_path("mashiro"))
prov = TsukasaProvider()

for key, line in LINES.items():
    for seed in range(1, 3):
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
