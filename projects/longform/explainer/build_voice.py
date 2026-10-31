#!/usr/bin/env python
"""作品の声を 1 キュー 1 ファイルで作る（プロセスは 1 つ＝モデルのロードは 1 回）。

bin/scene.py は全キューを 1 本に連結するが、キューごとに利得を掛けたい
（声量は生成後の WAV のレベル差に出ない）ので、連結せず voice/<name>.wav と
.params.yaml を残し、並べるのは assemble.py に任せる。

  PYTHONPATH=. <venv> .../build_voice.py --dir projects/longform/explainer [--force]
"""
from __future__ import annotations

import argparse
import datetime
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))))

import yaml

from semantic_audio_loom import config
from semantic_audio_loom.engine import AudioAssetEngine
from semantic_audio_loom.engine.store import save as store_save
from semantic_audio_loom.scene import load_scene
from semantic_audio_loom.skills.character_voice import (
    build_intent,
    character_path,
    load_voice_profile,
)

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))          # リポジトリの根
TIMINGS = os.path.join(config.project_dir("longform"), "timings.tsv")
# 作品の置き場（script.yaml のある dir）。explainer も drama もこの道具で作る。
WORK = HERE
SCRIPT = os.path.join(WORK, "script.yaml")
OUT = ""   # main() で --dir から決める


def _metadata(cue, audio) -> dict:
    return {
        "kind": "cue",
        "name": cue.name,
        "character": cue.character,
        "sample_rate": audio.sample_rate,
        "duration_sec": round(float(len(audio.wav)) / audio.sample_rate, 3),
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


def _timing(cue, wall: float, audio_s: float, rc: int) -> str:
    perf = ",".join(f"{k}={v}" for k, v in sorted(cue.performance.items()))
    settings = f"emotion={cue.emotion},intensity={cue.intensity},{perf},seed={cue.seed}"
    return "\t".join([
        "2026-10-31", "P3" if "explainer" in OUT else "P4",
        f"{os.path.basename(os.path.dirname(OUT))}/voice/{cue.name}", "tsukasa", settings,
        f"{wall:.0f}", f"{audio_s:.2f}", "M2Pro-16GB", f"rc={rc}",
    ])


def main() -> None:
    global SCRIPT, OUT, WORK
    ap = argparse.ArgumentParser()
    ap.add_argument("--force", action="store_true", help="既にある WAV も作り直す")
    ap.add_argument("--dir", default=WORK, help="作品の置き場（script.yaml の親）")
    args = ap.parse_args()

    WORK = os.path.abspath(args.dir)
    SCRIPT = os.path.join(WORK, "script.yaml")
    OUT = os.path.join(config.project_dir("longform"), "assets",
                       os.path.basename(WORK.rstrip("/")), "voice")

    scene = load_scene(SCRIPT)
    os.makedirs(OUT, exist_ok=True)
    engine = AudioAssetEngine(provider_name="tsukasa", resolve_mode="rule", lang="ja")

    rows = []
    for cue in scene.cues:
        name = cue.name or f"cue_{len(rows):02d}"
        path = os.path.join(OUT, name + ".wav")
        if os.path.exists(path) and not args.force:
            print(f"skip {name}")
            continue
        vp = load_voice_profile(character_path(cue.character))
        seed = cue.seed if cue.seed is not None else 1
        intent = build_intent(
            vp, cue.line, cue.emotion, cue.intensity, cue.performance,
            situation=cue.situation, subtext=cue.subtext, seed=seed,
        )
        started = time.time()
        asset = engine.generate(intent)
        wall = time.time() - started
        audio_s = float(len(asset.audio.wav)) / asset.audio.sample_rate
        params = dict(asset.parameters)
        params["name"] = name
        params["character"] = cue.character
        params["pause_before"] = cue.pause_before if cue.pause_before is not None else scene.default_pause
        store_save(asset.audio, _metadata(cue, asset.audio), params, OUT, name)
        rows.append(_timing(cue, wall, audio_s, 0))
        print(f"{name} {audio_s:5.2f}s wall={wall:4.1f}s")

    if rows:
        header = not os.path.exists(TIMINGS) or os.path.getsize(TIMINGS) == 0
        with open(TIMINGS, "a", encoding="utf-8") as f:
            if header:
                f.write("date\tstage\tasset\tmodel\tsettings\twall_s\taudio_s\tmachine\tnote\n")
            f.write("\n".join(rows) + "\n")
    print("done", len(rows))


if __name__ == "__main__":
    main()
