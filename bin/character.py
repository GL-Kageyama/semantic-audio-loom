#!/usr/bin/env python
"""CLI（Step 1 — キャラ作り）: キャラクターの声を定義・検証・一覧する。

キャラ資材は `characters/<name>.voice.yaml`（voice_profile.schema.json 準拠）。
ここで作ったキャラを、声の生成（bin/generate.py --character <name>）が名前で
再利用する。生成した音声（資材）とは別に、このキャラ資材だけを永続・共有する。

コマンド:
  bin/character.py init <name>     # テンプレートを characters/ に作成
  bin/character.py validate <name> # スキーマ検証
  bin/character.py list            # 登録済みキャラ一覧
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from semantic_audio_loom import config, i18n
from semantic_audio_loom.engine import validate
from semantic_audio_loom.skills.character_voice import character_path, list_characters, load_voice_profile


def cmd_init(args) -> None:
    os.makedirs(config.CHARACTERS_DIR, exist_ok=True)
    path = os.path.join(config.CHARACTERS_DIR, args.name + ".voice.yaml")
    if os.path.exists(path):
        print(args.t("character", "already_exists", "既に存在します: {path}（上書きしません）", path=path))
        return
    with open(path, "w", encoding="utf-8") as f:
        f.write(args.loc["character"]["template"].format(name=args.name))
    print(args.t("character", "created", "作成しました: {path}", path=path))
    print(args.t("character", "hint_validate", "内容を編集したら `bin/character.py validate {name}` で検証してください。", name=args.name))


def cmd_validate(args) -> None:
    profile = load_voice_profile(character_path(args.name))
    validate.validate_voice_profile(profile)
    print(f"OK: {args.name}")


def cmd_list(args) -> None:
    names = list_characters()
    if not names:
        print(args.t("character", "empty", "（キャラなし）"))
        return
    for n in names:
        print(n)


def main() -> None:
    lang, loc, t = i18n.translator()
    p = argparse.ArgumentParser(description=t("character", "description", "キャラクターの声を定義・検証・一覧する。"))
    i18n.add_lang_argument(p)
    sub = p.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help=t("character", "help_init", "テンプレートを characters/ に作成"))
    p_init.add_argument("name")
    p_init.set_defaults(func=cmd_init)

    p_val = sub.add_parser("validate", help=t("character", "help_validate", "スキーマ検証"))
    p_val.add_argument("name")
    p_val.set_defaults(func=cmd_validate)

    p_list = sub.add_parser("list", help=t("character", "help_list", "登録済みキャラ一覧"))
    p_list.set_defaults(func=cmd_list)

    args = p.parse_args()
    args.lang, args.loc, args.t = lang, loc, t
    args.func(args)


if __name__ == "__main__":
    main()
