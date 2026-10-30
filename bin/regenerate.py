#!/usr/bin/env python
"""CLI: params.yaml から同じ Spec・同じ seed で再生成する（再現性の確認用）。

Resolve（LLM）は呼ばず、保存済みの performance_spec をそのまま使う。
例:
  bin/regenerate.py output/mashiro_morning.params.yaml --out-dir output_regen
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml

from semantic_audio_loom import i18n
from semantic_audio_loom.engine import AudioAssetEngine
from semantic_audio_loom.types import GenerationRequest


def main() -> None:
    p = argparse.ArgumentParser(description="Regenerate from params.yaml.")
    i18n.add_lang_argument(p)
    p.add_argument("params", help="path to .params.yaml")
    p.add_argument("--out-dir", default="output_regen")
    p.add_argument("--name", default=None)
    args = p.parse_args()

    with open(args.params, encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    params = doc["parameters"]
    name = args.name or doc.get("name") or "asset"

    asset_type = params.get("asset_type", "voice")
    # voice params は performance_spec、非 voice は spec に Spec を持つ。
    spec = params.get("spec") or params["performance_spec"]
    # Spec にも seed にも入らない設定は params に写してある。書き戻さないと
    # 「同じ params から同じ音」が崩れる（stable_audio のサンプリング回数）。
    settings = params.get("provider_settings") or {}
    if settings.get("steps"):
        os.environ["SAL_STABLE_AUDIO_STEPS"] = str(settings["steps"])
    request = GenerationRequest(
        asset_type=asset_type,
        voice_profile=params.get("voice_profile", {}),
        spec=spec,
        dialogue=params.get("dialogue", ""),
        reading=params.get("reading", ""),
        seed=params["seed"],
        quality="high",
        duration=params.get("duration"),
        provider_hint=params.get("provider"),
    )
    engine = AudioAssetEngine(provider_name=params.get("provider"))
    asset = engine.generate_request(request, out_dir=args.out_dir, name=name)

    print("wav:", asset.path)
    print("seed:", asset.parameters["seed"])


if __name__ == "__main__":
    main()
