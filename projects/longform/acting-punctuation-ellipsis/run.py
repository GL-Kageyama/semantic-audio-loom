"""文末が「…」のとき、声はどうなるか。

    PYTHONPATH=. $PY projects/longform/acting-punctuation-ellipsis/run.py

脚本では「言いよどみ」を「…」で書く。句点（`。`）と比べて、声がどう変わるかを
測る。`。` の側は `acting-punctuation/` の `pn-period-s1..5`（同じ行・同じ Spec・
同じ seed）をそのまま使うので、ここでは `…` の 5 本だけ焼く。
出す先は `projects/longform/assets/acting-punctuation-ellipsis/voice/`。
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

OUT = "projects/longform/assets/acting-punctuation-ellipsis/voice"
config.ALPHA, config.BETA = 0.35, 0.7
os.makedirs(OUT, exist_ok=True)

LINE = "明日、また来るね…"

base = json.load(open("projects/longform/acting-subtext/llm-specs.json"))["none"]["spec"]
vp = load_voice_profile(character_path("mashiro"))
prov = TsukasaProvider()

for seed in range(1, 6):
    path = os.path.join(OUT, f"pe-ellipsis-s{seed}.wav")
    if os.path.exists(path):
        continue
    req = GenerationRequest(
        asset_type="voice", spec=base, seed=seed, voice_profile=vp, dialogue=LINE,
    )
    audio = prov.generate(req)
    sf.write(path, np.asarray(audio.wav, dtype=np.float32), config.SAMPLE_RATE)
    print("wrote", path, flush=True)
print("done")
