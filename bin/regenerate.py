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

    request = GenerationRequest(
        asset_type="voice",
        voice_profile=params["voice_profile"],
        performance_spec=params["performance_spec"],
        dialogue=params["dialogue"],
        seed=params["seed"],
        quality="high",
        provider_hint=params.get("provider"),
    )
    engine = AudioAssetEngine(provider_name=params.get("provider"))
    asset = engine.generate_request(request, out_dir=args.out_dir, name=name)

    print("wav:", asset.path)
    print("seed:", asset.parameters["seed"])


if __name__ == "__main__":
    main()
