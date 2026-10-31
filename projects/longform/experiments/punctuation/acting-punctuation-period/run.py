"""途中の句点は、短い行でも効きを弱めるか。

    PYTHONPATH=. $PY projects/longform/experiments/punctuation/acting-punctuation-period/run.py

`experiments/punctuation/acting-punctuation-long/` では、24 文字の同じ行で途中の句点を読点に替えると
`！` の効きが +13.2 → +22.0 Hz に戻った。長さが同じでも効いたので、原因は
途中の句点らしい。**行を短くしたまま**途中の句点を入れて、それを直接見る。
「明日。また来るね」の末尾だけを `。` / `！` に振る（2 通り × seed 5 = 10 本）。
対照は同じ話者の「明日、また来るね」（`experiments/punctuation/acting-punctuation/` の +39.3 Hz）。
出す先は `projects/longform/assets/acting-punctuation-period/voice/`。
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

OUT = "projects/longform/assets/acting-punctuation-period/voice"
config.ALPHA, config.BETA = 0.35, 0.7
os.makedirs(OUT, exist_ok=True)

STEM = "明日。また来るね"
LINES = {
    "period": STEM + "。",
    "exclaim": STEM + "！",
}

base = json.load(open("projects/longform/experiments/subtext/acting-subtext/llm-specs.json"))["none"]["spec"]
vp = load_voice_profile(character_path("mashiro"))
prov = TsukasaProvider()

for key, line in LINES.items():
    for seed in range(1, 6):
        path = os.path.join(OUT, f"pp-{key}-s{seed}.wav")
        if os.path.exists(path):
            continue
        req = GenerationRequest(
            asset_type="voice", spec=base, seed=seed, voice_profile=vp, dialogue=line,
        )
        audio = prov.generate(req)
        sf.write(path, np.asarray(audio.wav, dtype=np.float32), config.SAMPLE_RATE)
        print("wrote", path, flush=True)
print("done")
