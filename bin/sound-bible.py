#!/usr/bin/env python
"""CLI: Sound Bible（作品の音響スタイル）を作る・見る・検証する。

  bin/sound-bible.py init demo
  bin/sound-bible.py show demo
  bin/sound-bible.py validate demo

置き場は projects/<project>/sound-bible.yaml。bin/asset.py はこのファイルが
あれば自動で読み、Direction の未指定フィールド（style / palette / negative）を補う。
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml

from semantic_audio_loom import i18n
from semantic_audio_loom.engine import validate
from semantic_audio_loom.skills.sound import bible_path

_TEMPLATE = """\
project: {project}
notes: ""

music:
  style: []
  instrumentation: []
  negative: []

ambience:
  style: []
  palette: []
  negative: []

sfx:
  style: []
  palette: []
  negative: []

foley:
  style: []
  palette: []
  negative: []

dialogue:
  style: []
  negative: []
"""


_SECTIONS = ("music", "ambience", "sfx", "foley", "dialogue")


def _load(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def _filled_fields(doc: dict) -> int:
    """中身のある欄の数。0 なら全節が空（＝検証しても意味がない）。"""
    count = 0
    for section in _SECTIONS:
        for value in (doc.get(section) or {}).values():
            if value:
                count += 1
    return count


def main() -> None:
    lang, loc, t = i18n.translator()
    p = argparse.ArgumentParser(description=t("sound_bible", "description", "Sound Bible を操作する。"))
    i18n.add_lang_argument(p)
    sub = p.add_subparsers(dest="cmd", required=True)

    s = sub.add_parser("init", help=t("sound_bible", "help_init", "テンプレートを書く"))
    s.add_argument("project")
    s.add_argument("--force", action="store_true")

    s = sub.add_parser("show", help=t("sound_bible", "help_show", "表示"))
    s.add_argument("project")

    s = sub.add_parser("validate", help=t("sound_bible", "help_validate", "検証"))
    s.add_argument("project")

    args = p.parse_args()
    path = bible_path(args.project)

    if args.cmd == "init":
        if os.path.exists(path) and not args.force:
            raise SystemExit(t("sound_bible", "exists", "既にあります（--force で上書き）: {path}", path=path))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(_TEMPLATE.format(project=args.project))
        print("written:", path)
        return

    if not os.path.exists(path):
        raise SystemExit(t("sound_bible", "not_found", "見つかりません: {path}", path=path))
    doc = _load(path)

    if args.cmd == "show":
        print(yaml.safe_dump(doc, allow_unicode=True, sort_keys=False))
        return

    if args.cmd == "validate":
        try:
            validate.validate_sound_bible(doc)
        except Exception as exc:
            print("NG", exc)
            raise SystemExit(1)
        if not _filled_fields(doc):
            # スキーマに通っても全節が空なら「健全」とは言わない。
            print(t("sound_bible", "valid_empty", "Sound Bible は空です（全節が未設定）: {path}",
                    path=path))
            return
        print(t("sound_bible", "valid", "Sound Bible は健全です。"))
        print(f"filled: {_filled_fields(doc)}")


if __name__ == "__main__":
    main()
