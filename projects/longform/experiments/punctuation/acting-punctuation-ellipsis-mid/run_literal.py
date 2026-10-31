"""途中の「…」が「、」に置き換わることを、字面で確かめる。

    PYTHONPATH=. $PY projects/longform/experiments/punctuation/acting-punctuation-ellipsis-mid/run_literal.py

`normalize_ellipsis()` は文中の `…` を `、` にする。だから
`明日、……また来るね` は `明日、、また来るね` になる。同じ字面を**省略記号なしで**
焼いて、`pm-ellipsis-*` と md5 まで一致するかを見る。
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

LINE = "明日、、また来るね"

base = json.load(open("projects/longform/experiments/subtext/acting-subtext/llm-specs.json"))["none"]["spec"]
vp = load_voice_profile(character_path("mashiro"))
prov = TsukasaProvider()

for seed in range(1, 6):
    path = os.path.join(OUT, f"pm-literal-s{seed}.wav")
    if os.path.exists(path):
        continue
    req = GenerationRequest(
        asset_type="voice", spec=base, seed=seed, voice_profile=vp, dialogue=LINE,
    )
    audio = prov.generate(req)
    sf.write(path, np.asarray(audio.wav, dtype=np.float32), config.SAMPLE_RATE)
    print("wrote", path, flush=True)
print("done")
