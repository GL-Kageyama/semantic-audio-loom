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

from semantic_audio_loom import config
from semantic_audio_loom.engine import validate
from semantic_audio_loom.skills.character_voice import character_path, list_characters, load_voice_profile

_TEMPLATE = """# {name} — キャラクターの声（キャラ資材）。
# voice_profile.schema.json 準拠。reference_audio は参照音声ライブラリの話者キー
# か実ファイルパス（経路A: timbre をこの音声から固定する）。
character: {name}
# reference_audio: female_young_p308   # 例。話者キーは参照音声ライブラリから選ぶ
voice:
  age: young_adult      # child / adolescent / young_adult / adult / middle_aged / elderly
  gender: female        # female / male（プロンプト主語と参照ファイル名判定に使う）
  pitch: medium_high    # very_low / low / medium_low / medium / medium_high / high / very_high
  texture: soft         # soft / warm / clear / bright / dark / husky / breathy / neutral
  breathiness: slight   # none / slight / moderate / heavy
  resonance: head       # intimate / chest / head / nasal / bright / neutral
"""


def cmd_init(args) -> None:
    os.makedirs(config.CHARACTERS_DIR, exist_ok=True)
    path = os.path.join(config.CHARACTERS_DIR, args.name + ".voice.yaml")
    if os.path.exists(path):
        print(f"既に存在します: {path}（上書きしません）")
        return
    with open(path, "w", encoding="utf-8") as f:
        f.write(_TEMPLATE.format(name=args.name))
    print(f"作成しました: {path}")
    print("内容を編集したら `bin/character.py validate %s` で検証してください。" % args.name)


def cmd_validate(args) -> None:
    profile = load_voice_profile(character_path(args.name))
    validate.validate_voice_profile(profile)
    print(f"OK: {args.name}")


def cmd_list(args) -> None:
    names = list_characters()
    if not names:
        print("（キャラなし）")
        return
    for n in names:
        print(n)


def main() -> None:
    p = argparse.ArgumentParser(description="キャラクターの声を定義・検証・一覧する。")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="テンプレートを characters/ に作成")
    p_init.add_argument("name")
    p_init.set_defaults(func=cmd_init)

    p_val = sub.add_parser("validate", help="スキーマ検証")
    p_val.add_argument("name")
    p_val.set_defaults(func=cmd_validate)

    p_list = sub.add_parser("list", help="登録済みキャラ一覧")
    p_list.set_defaults(func=cmd_list)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
