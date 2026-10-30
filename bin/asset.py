#!/usr/bin/env python
"""CLI: 非 voice の音響資材（bgm / ambience / sfx / foley）を生成する。

声の 7 段フローと同じ経路を通る（Validate → Route → Resolve → Generate →
Normalize → Tag → Store）。Direction は `--sound key=value` で書く。

例:
  bin/asset.py --type bgm --project demo --name lonely-room \\
      --sound role=underscore --sound mood=lonely,sparse \\
      --sound instrumentation=solo_piano --sound duration=20

  bin/asset.py --type ambience --project demo --name station-night \\
      --sound environment="empty train station" --sound time=night --duration 30

  bin/asset.py --type sfx --project demo --name door-close \\
      --sound event="heavy wooden door closing" --duration 3

生成物は projects/<project>/assets/<scene>/ に置く。再利用するなら --save-library NAME。
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from semantic_audio_loom import config, i18n
from semantic_audio_loom.engine import AudioAssetEngine
from semantic_audio_loom.skills import library
from semantic_audio_loom.skills.sound import (
    LIST_KEYS,
    apply_bible,
    bible_path,
    build_intent,
    load_bible,
)
from semantic_audio_loom.types import SOUND_TYPES


def _parse_value(raw: str):
    try:
        return json.loads(raw)
    except Exception:
        pass
    if "," in raw:
        return [part.strip() for part in raw.split(",") if part.strip()]
    return raw


def _parse_pairs(pairs: list[str] | None) -> dict:
    out = {}
    for pair in pairs or []:
        if "=" not in pair:
            raise SystemExit(f"--sound expects key=value, got: {pair!r}")
        key, value = pair.split("=", 1)
        key = key.strip()
        parsed = _parse_value(value)
        if key in LIST_KEYS and not isinstance(parsed, list):
            parsed = [parsed]
        out[key] = parsed
    return out


def _load_sound_file(path: str) -> dict:
    import yaml

    with open(path, encoding="utf-8") as f:
        if path.endswith(".json"):
            return json.load(f) or {}
        return yaml.safe_load(f) or {}


def main() -> None:
    lang, loc, t = i18n.translator()
    p = argparse.ArgumentParser(description=t("asset", "description", "BGM・環境音・効果音・フォーリーを生成する。"))
    i18n.add_lang_argument(p)
    p.add_argument("--type", required=True, choices=list(SOUND_TYPES))
    p.add_argument("--project", default="demo", help=t("asset", "help_project", "保存先 projects/<project>/assets/"))
    p.add_argument("--scene", default="sound", help=t("asset", "help_scene", "保存先サブフォルダ"))
    p.add_argument("--sound", action="append", default=[], metavar="KEY=VALUE",
                   help=t("asset", "help_sound", "Sound Direction（複数可。カンマ区切りは配列）"))
    p.add_argument("--sound-file", default=None, help=t("asset", "help_sound_file", "Sound Direction の YAML/JSON"))
    p.add_argument("--prompt", default=None, help=t("asset", "help_prompt", "モデル向けプロンプト（英語）を直接指定"))
    p.add_argument("--duration", type=float, default=None)
    p.add_argument("--situation", default="", help=t("asset", "help_situation", "状況（Resolve の入力）"))
    p.add_argument("--subtext", default="", help=t("asset", "help_subtext", "意図の裏（任意）"))
    p.add_argument("--bible", default=None, help=t("asset", "help_bible", "Sound Bible のパス（既定は projects/<project>/sound-bible.yaml）"))
    p.add_argument("--no-bible", action="store_true")
    p.add_argument("--resolve", choices=("llm", "rule"), default="llm")
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--name", default=None)
    p.add_argument("--provider", default=None)
    p.add_argument("--save-library", default=None, metavar="NAME",
                   help=t("asset", "help_save_library", "library/<type>/<NAME> に取り込む"))
    p.add_argument("--tags", default=None, help=t("asset", "help_tags", "ライブラリのタグ（カンマ区切り）"))
    p.add_argument("--license", default="", help=t("asset", "help_license", "ライセンス表記"))
    p.add_argument("--attribution", default="", help=t("asset", "help_attribution", "帰属表示"))
    args = p.parse_args()

    sound = _load_sound_file(args.sound_file) if args.sound_file else {}
    sound.update(_parse_pairs(args.sound))
    if args.prompt:
        sound["prompt"] = args.prompt
    if args.duration is not None:
        sound["duration"] = args.duration

    bible_file = args.bible or bible_path(args.project)
    if not args.no_bible and os.path.exists(bible_file):
        sound = apply_bible(args.type, load_bible(bible_file), sound)

    intent = build_intent(
        args.type,
        sound=sound,
        situation=args.situation,
        scene={"name": args.scene},
        subtext=args.subtext,
        seed=args.seed,
    )

    name = args.name or args.type
    out_dir = os.path.join(config.project_dir(args.project), "assets", args.scene)
    engine = AudioAssetEngine(provider_name=args.provider, resolve_mode=args.resolve, lang=lang)
    asset = engine.generate(intent, out_dir=out_dir, name=name)

    print("wav:", asset.path)
    print("seed:", asset.parameters["seed"])
    print("spec:", json.dumps(asset.parameters["spec"], ensure_ascii=False))
    print("metadata:", json.dumps(asset.metadata, ensure_ascii=False))

    library_name = args.save_library
    if library_name:
        tags = [tag.strip() for tag in (args.tags or "").split(",") if tag.strip()]
        doc = library.add_generated(
            asset,
            asset_type=args.type,
            name=library_name,
            tags=tags,
            license=args.license,
            attribution=args.attribution,
        )
        print("library:", library.asset_path(args.type, library_name))
        print("duration:", doc.get("duration"), "s")


if __name__ == "__main__":
    main()
