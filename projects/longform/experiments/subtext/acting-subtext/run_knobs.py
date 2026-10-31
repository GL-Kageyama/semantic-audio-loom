"""subtext の解決で動いた 2 欄だけを、1 つずつ振る（4 通り × seed 5 = 20 本）。

    PYTHONPATH=. $PY projects/longform/experiments/subtext/acting-subtext/run_knobs.py

基準は `llm-specs.json` の `none` の Spec。そこから
  - `prosody.intonation`（neutral / wavering）
  - `emotion.intensity`（0.5 = 句なし / 0.4 = 「faint」の句）
だけを変える。ほかの欄はすべて同じ。出す先は
`projects/longform/assets/acting-subtext-knobs/voice/`。
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

HERE = "projects/longform/experiments/subtext/acting-subtext"
OUT = "projects/longform/assets/acting-subtext-knobs/voice"
LINE = "明日、また来るね。"

config.ALPHA, config.BETA = 0.35, 0.7
os.makedirs(OUT, exist_ok=True)

base = json.load(open(os.path.join(HERE, "llm-specs.json")))["none"]["spec"]
vp = load_voice_profile(character_path("mashiro"))
prov = TsukasaProvider()

for intonation in ("neutral", "wavering"):
    for intensity in (0.5, 0.4):
        spec = copy.deepcopy(base)
        spec.setdefault("prosody", {})["intonation"] = intonation
        spec.setdefault("emotion", {})["intensity"] = intensity
        name = f"kb-{intonation}-i{int(intensity * 100)}"
        for seed in range(1, 6):
            path = os.path.join(OUT, f"{name}-s{seed}.wav")
            if os.path.exists(path):
                continue
            req = GenerationRequest(
                asset_type="voice", spec=spec, seed=seed,
                voice_profile=vp, dialogue=LINE,
            )
            audio = prov.generate(req)
            sf.write(path, np.asarray(audio.wav, dtype=np.float32), config.SAMPLE_RATE)
            print("wrote", path, flush=True)
print("done")
