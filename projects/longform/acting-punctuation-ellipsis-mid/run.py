"""文の途中の「…」は、消されるか。

    PYTHONPATH=. $PY projects/longform/acting-punctuation-ellipsis-mid/run.py

文末の `…` は正規化で消え、`なし` と同じ音になった
（`acting-punctuation-ellipsis/`）。途中に置いた `…` も同じかを見る。
行は `明日、……また来るね`。`…` が消えれば `明日、また来るね`（`なし`）と
同じ音になるはず。比べる側は `acting-punctuation/` の `pn-none-s1..5`
（同じ Spec・同じ seed）を使う。
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

LINE = "明日、……また来るね"

base = json.load(open("projects/longform/acting-subtext/llm-specs.json"))["none"]["spec"]
vp = load_voice_profile(character_path("mashiro"))
prov = TsukasaProvider()

for seed in range(1, 6):
    path = os.path.join(OUT, f"pm-ellipsis-s{seed}.wav")
    if os.path.exists(path):
        continue
    req = GenerationRequest(
        asset_type="voice", spec=base, seed=seed, voice_profile=vp, dialogue=LINE,
    )
    audio = prov.generate(req)
    sf.write(path, np.asarray(audio.wav, dtype=np.float32), config.SAMPLE_RATE)
    print("wrote", path, flush=True)
print("done")
