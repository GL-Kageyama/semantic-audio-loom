#!/usr/bin/env python
"""CLI（Step 1.5 — 演技の振り付け）: 演技指示を定義・検証・一覧する。

演技資材は `performances/<name>.direction.yaml`（performance_asset.schema.json 準拠）。
「どう演じるか」（感情・声量・速度・delivery などの Direction）を名前で再利用する。
キャラ資材（characters/）が「誰の声か」を持つのに対し、こちらは「どう演じるか」を持ち、
声の生成（bin/generate.py --performance <name>）が組み合わせて参照する。

コマンド:
  bin/performance.py init <name>       # テンプレートを performances/ に作成
  bin/performance.py validate <name>   # スキーマ検証
  bin/performance.py list              # 登録済み演技一覧
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from semantic_audio_loom import config, i18n
from semantic_audio_loom.engine import validate
from semantic_audio_loom.skills.performance import list_performances, load_direction, performance_path


def cmd_init(args) -> None:
    os.makedirs(config.PERFORMANCES_DIR, exist_ok=True)
    path = os.path.join(config.PERFORMANCES_DIR, args.name + ".direction.yaml")
    if os.path.exists(path):
        print(args.t("performance", "already_exists", "既に存在します: {path}（上書きしません）", path=path))
        return
    with open(path, "w", encoding="utf-8") as f:
        f.write(args.loc["performance"]["template"].format(name=args.name))
    print(args.t("performance", "created", "作成しました: {path}", path=path))
    print(args.t("performance", "hint_validate", "内容を編集したら `bin/performance.py validate {name}` で検証してください。", name=args.name))


def cmd_validate(args) -> None:
    direction = load_direction(performance_path(args.name))
    validate.validate_performance_asset(direction)
    print(f"OK: {args.name}")


def cmd_list(args) -> None:
    names = list_performances()
    if not names:
        print(args.t("performance", "empty", "（演技なし）"))
        return
    for n in names:
        print(n)


def main() -> None:
    lang, loc, t = i18n.translator()
    p = argparse.ArgumentParser(description=t("performance", "description", "演技の振り付けを定義・検証・一覧する。"))
    i18n.add_lang_argument(p)
    sub = p.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help=t("performance", "help_init", "テンプレートを performances/ に作成"))
    p_init.add_argument("name")
    p_init.set_defaults(func=cmd_init)

    p_val = sub.add_parser("validate", help=t("performance", "help_validate", "スキーマ検証"))
    p_val.add_argument("name")
    p_val.set_defaults(func=cmd_validate)

    p_list = sub.add_parser("list", help=t("performance", "help_list", "登録済み演技一覧"))
    p_list.set_defaults(func=cmd_list)

    args = p.parse_args()
    args.lang, args.loc, args.t = lang, loc, t
    args.func(args)


if __name__ == "__main__":
    main()
