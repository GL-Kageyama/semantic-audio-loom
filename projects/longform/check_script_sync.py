#!/usr/bin/env python
"""台本（script.yaml）と、焼いてある声（voice/*.params.yaml）が同じかを突き合わせる。

`build_voice.py` は既にある WAV を飛ばすので、**台本を直しても音は黙って古いまま**に
なる。ここでは台本から Spec を組み直し（モデルは読まない）、保存済みの params と
1 欄ずつ比べる。

  PYTHONPATH=. <venv> projects/longform/check_script_sync.py --dir projects/longform/drama

出るもの：合っていれば `OK 89/89`。食い違えば cue 名と欄、params の値、台本の値。
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import yaml

from semantic_audio_loom import config
from semantic_audio_loom.engine import resolve
from semantic_audio_loom.scene import load_scene
from semantic_audio_loom.skills.character_voice import build_intent, character_path, load_voice_profile


def _flat(d, prefix=""):
    """入れ子の dict を `a/b/c` の平らな形にする（比べるため）。"""
    out = {}
    if isinstance(d, dict):
        for k, v in d.items():
            out.update(_flat(v, f"{prefix}{k}/") if isinstance(v, dict) else {f"{prefix}{k}": v})
    else:
        out[prefix.rstrip("/")] = d
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True, help="script.yaml のある dir")
    ap.add_argument("--quiet", action="store_true", help="食い違いだけ出す")
    args = ap.parse_args()

    work = os.path.abspath(args.dir)
    script = os.path.join(work, "script.yaml")
    voice = os.path.join(config.project_dir("longform"), "assets",
                         os.path.basename(work.rstrip("/")), "voice")
    scene = load_scene(script)
    with open(script, encoding="utf-8") as f:
        doc = {c.get("name"): c for c in (yaml.safe_load(f) or {}).get("cues", []) if c}

    bad = []
    ok = 0
    for cue in scene.cues:
        name = cue.name
        path = os.path.join(voice, name + ".params.yaml")
        if not os.path.exists(path):
            bad.append((name, "params", "（無い）", "ある"))
            continue
        with open(path, encoding="utf-8") as f:
            saved = yaml.safe_load(f) or {}
        got = saved.get("parameters") or {}
        vp = load_voice_profile(character_path(cue.character))
        intent = build_intent(vp, cue.line, cue.emotion, cue.intensity, cue.performance,
                              situation=cue.situation, subtext=cue.subtext,
                              seed=cue.seed if cue.seed is not None else 1)
        # 焼いたときと同じ経路（rule）で Spec を組み直す。モデルは読まない。
        want = resolve.resolve(intent, mode="rule", lang="ja")
        have = got.get("performance_spec") or {}
        kw, kh = _flat(want), _flat(have)
        diffs = []
        for k in sorted(set(kw) | set(kh)):
            if kw.get(k) != kh.get(k):
                diffs.append((k, kh.get(k), kw.get(k)))
        if got.get("dialogue") != intent.dialogue:
            diffs.append(("dialogue", got.get("dialogue"), intent.dialogue))
        knobs = doc.get(name) or {}
        for k, want_v in (("seed", cue.seed if cue.seed is not None else 1),
                          ("alpha", float(knobs["alpha"]) if "alpha" in knobs else None),
                          ("beta", float(knobs["beta"]) if "beta" in knobs else None)):
            if want_v is not None and got.get(k) != want_v:
                diffs.append((k, got.get(k), want_v))
        if diffs:
            bad.append((name, diffs))
        else:
            ok += 1

    if not args.quiet:
        print(f"{len(scene.cues)} 本 / 一致 {ok} / 食い違い {len(bad)}")
    for name, diffs in bad:
        if isinstance(diffs, str):
            print(f"  {name}: {diffs}")
            continue
        for k, got_v, want_v in diffs:
            print(f"  {name}  {k}  params={got_v!r}  台本={want_v!r}")
    return 0 if not bad else 1


if __name__ == "__main__":
    raise SystemExit(main())
