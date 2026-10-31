"""台詞の裏の意味を、表を通さず**自由文**でプロンプトに足したら声は動くか。

    PYTHONPATH=. $PY projects/longform/acting-freetext/run.py

`_spec_prompt` は固定の語表（emotion / delivery / 強度 / 速さ / pitch / 抑揚）しか
散文にしない。ここでは同じ Spec の散文に、**表に無い一文**を足して焼く。
5 通り × seed 5 = 25 本。出す先は `projects/longform/assets/acting-freetext/voice/`。
"""
import json
import os
import random
import sys

sys.path.insert(0, os.getcwd())

import numpy as np
import soundfile as sf
import torch

from semantic_audio_loom import config
from semantic_audio_loom.providers import tsukasa as P
from semantic_audio_loom.skills.character_voice import character_path, load_voice_profile

HERE = "projects/longform/acting-freetext"
OUT = "projects/longform/assets/acting-freetext/voice"
LINE = "明日、また来るね。"

config.ALPHA, config.BETA = 0.35, 0.7
os.makedirs(OUT, exist_ok=True)

base = json.load(open("projects/longform/acting-subtext/llm-specs.json"))["none"]["spec"]
vp = load_voice_profile(character_path("mashiro"))
ref = vp.get("reference_audio") or (vp.get("voice") or {}).get("reference_audio")

ADD = {
    "none": "",
    "cry": "She is holding back tears.",
    "furious": "She is furious but hiding it.",
    "smile": "She is smiling as she says it.",
    "afraid": "She is afraid of the answer.",
}

P._load_model()
T = P._T
subj = P._subject(vp)
line = P._phonemize(LINE)

with torch.no_grad():
    timbre = T.compute_style_through_clip(P._resolve_reference(ref))[:, :128]

for key, extra in ADD.items():
    prompt = P._spec_prompt(subj, base) + (" " + extra if extra else "")
    print(f"### {key}: {prompt}", flush=True)
    with torch.no_grad():
        prosody = T.Kotodama_Prompter(T.model, prompt, T.device)[:, 128:]
    ref_s = torch.cat([timbre, prosody], dim=1)
    for seed in range(1, 6):
        path = os.path.join(OUT, f"ft-{key}-s{seed}.wav")
        if os.path.exists(path):
            continue
        torch.manual_seed(seed)
        np.random.seed(seed)
        random.seed(seed)
        wav = T.inference(line, ref_s=ref_s, alpha=config.ALPHA, beta=config.BETA,
                          rate_of_speech=1.0)
        wav = np.asarray(wav).squeeze().astype(np.float32)
        sf.write(path, wav, config.SAMPLE_RATE)
        print("wrote", path, flush=True)
print("done")
