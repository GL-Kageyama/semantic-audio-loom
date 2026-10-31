"""同じプロセスの中で、同じ Spec・同じ seed を N 回作り、md5 を並べる。

    PYTHONPATH=. $PY projects/longform/determinism/within_process.py 10

cue は `pl-natural-s3`（`acting-pitch-ladder/` の natural × seed 3）。
1 本ごとに新しい Intent を作る（build_voice.py と同じ経路）。
"""
import hashlib
import os
import sys

sys.path.insert(0, os.getcwd())

import numpy as np

from semantic_audio_loom import config
from semantic_audio_loom.engine import AudioAssetEngine
from semantic_audio_loom.scene import load_scene
from semantic_audio_loom.skills.character_voice import (
    build_intent,
    character_path,
    load_voice_profile,
)

N = int(sys.argv[1]) if len(sys.argv) > 1 else 10
sc = load_scene("projects/longform/acting-pitch-ladder/script.yaml")
cue = next(c for c in sc.cues if c.name == "pl-natural-s3")

config.ALPHA, config.BETA = 0.35, 0.7
engine = AudioAssetEngine(provider_name="tsukasa", resolve_mode="rule", lang="ja")
vp = load_voice_profile(character_path(cue.character))


def build():
    intent = build_intent(
        vp, cue.line, cue.emotion, cue.intensity, cue.performance,
        situation=cue.situation, subtext=cue.subtext, seed=cue.seed,
    )
    wav = engine.generate(intent).audio.wav
    return np.asarray(wav, dtype=np.float32)


first = None
for i in range(1, N + 1):
    w = build()
    h = hashlib.md5(w.tobytes()).hexdigest()[:7]
    if first is None:
        first = w
    d = float(np.max(np.abs(w - first)))
    print(f"{i}\t{h}\t{d:.6f}")
