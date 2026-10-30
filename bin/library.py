#!/usr/bin/env python
"""CLI: 再利用ライブラリ（library/）の一覧・検索・表示・取り込み・検証。

  bin/library.py list [--type sfx]
  bin/library.py search "rain night" [--type ambience]
  bin/library.py show door-close [--type sfx]
  bin/library.py add path/to.wav --type sfx --name door-close --tags door,wood
  bin/library.py validate
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml

from semantic_audio_loom import i18n
from semantic_audio_loom.skills import library
from semantic_audio_loom.types import ASSET_TYPES


def _row(doc: dict) -> str:
    name = doc.get("name") or "?"
    asset_type = doc.get("asset_type") or "?"
    duration = doc.get("duration")
    duration_text = f"{duration:g}s" if isinstance(duration, (int, float)) else "-"
    tags = ",".join(doc.get("tags") or [])
    prompt = (doc.get("spec") or {}).get("prompt") or ""
    if len(prompt) > 60:
        prompt = prompt[:57] + "..."
    return f"{asset_type:<9} {name:<24} {duration_text:>8}  {tags:<20} {prompt}"


def _parse_semantic(pairs: list[str] | None) -> dict:
    out = {}
    for pair in pairs or []:
        if "=" not in pair:
            raise SystemExit(f"--semantic expects key=value, got: {pair!r}")
        key, value = pair.split("=", 1)
        out[key.strip()] = value
    return out


def main() -> None:
    lang, loc, t = i18n.translator()
    p = argparse.ArgumentParser(description=t("library", "description", "再利用ライブラリを操作する。"))
    i18n.add_lang_argument(p)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("list", help=t("library", "help_list", "一覧"))
    s.add_argument("--type", choices=list(ASSET_TYPES))

    s = sub.add_parser("search", help=t("library", "help_search", "意味タグ・プロンプトで検索"))
    s.add_argument("query", nargs="?", default="")
    s.add_argument("--type", choices=list(ASSET_TYPES))
    s.add_argument("--tags", default=None)

    s = sub.add_parser("show", help=t("library", "help_show", "1 件を YAML で表示"))
    s.add_argument("name")
    s.add_argument("--type", choices=list(ASSET_TYPES))

    s = sub.add_parser("add", help=t("library", "help_add", "WAV を取り込む"))
    s.add_argument("wav")
    s.add_argument("--type", required=True, choices=list(ASSET_TYPES))
    s.add_argument("--name", required=True)
    s.add_argument("--tags", default=None)
    s.add_argument("--prompt", default="")
    s.add_argument("--semantic", action="append", default=[], metavar="KEY=VALUE")
    s.add_argument("--license", default="")
    s.add_argument("--attribution", default="")

    sub.add_parser("validate", help=t("library", "help_validate", "全件を検証"))

    args = p.parse_args()

    if args.cmd == "list":
        docs = library.list_assets(args.type)
        if not docs:
            print(t("library", "empty", "ライブラリは空です: {path}", path=library.library_dir()))
            return
        for doc in docs:
            print(_row(doc))
        return

    if args.cmd == "search":
        tags = [x.strip() for x in (args.tags or "").split(",") if x.strip()]
        docs = library.search(args.query, asset_type=args.type, tags=tags)
        if not docs:
            print(t("library", "no_hits", "該当する資材がありません。"))
            return
        for doc in docs:
            print(_row(doc))
        return

    if args.cmd == "show":
        doc = library.find(args.name, args.type)
        if doc is None:
            raise SystemExit(t("library", "not_found", "資材が見つかりません: {name}", name=args.name))
        print(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False))
        return

    if args.cmd == "add":
        tags = [x.strip() for x in (args.tags or "").split(",") if x.strip()]
        doc = library.add_wav(
            args.wav,
            args.type,
            args.name,
            spec={"prompt": args.prompt} if args.prompt else {},
            semantic=_parse_semantic(args.semantic),
            tags=tags,
            license=args.license,
            attribution=args.attribution,
        )
        print("library:", library.asset_path(args.type, args.name))
        print("duration:", doc.get("duration"), "s")
        return

    if args.cmd == "validate":
        if not library.list_assets():
            # 0 件を「健全」と言わない（空の検査は何も検査していない）。
            print(t("library", "valid_empty", "検証する資材がありません（0 件）: {path}",
                    path=library.library_dir()))
            print(json.dumps({"assets": 0}, ensure_ascii=False))
            return
        problems = library.validate_all()
        if problems:
            for msg in problems:
                print("NG", msg)
            raise SystemExit(1)
        print(t("library", "valid", "ライブラリは健全です。"))
        print(json.dumps({"assets": len(library.list_assets())}, ensure_ascii=False))


if __name__ == "__main__":
    main()
