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

from semantic_audio_loom import config
from semantic_audio_loom.engine import validate
from semantic_audio_loom.skills.performance import list_performances, load_direction, performance_path

_TEMPLATE = """# {name} — 演技の振り付け（演技資材）。
# performance_asset.schema.json 準拠。emotion のみ必須。残りは省略可。
# situation/subtext は Resolve（LLM の subtext 推論）の入力になる。
emotion: neutral       # anxiety / sadness / anger / fear / joy / confidence / loneliness / excitement / calm / guilt / neutral
# intensity: moderate  # none / subtle / moderate / strong / overwhelming
# volume: normal       # whisper / quiet / normal / loud / shout
# speed: natural       # very_slow / slow / natural / fast / very_fast
# pitch: natural       # very_low / low / slightly_low / natural / slightly_high / high
# breathiness: none    # none / slight / moderate / heavy
# delivery: controlled # restrained / subtle / suppressed / controlled / flat / gentle / intimate / aggressive / cheerful / cold / desperate / hesitant
# pause_before: 0.0    # 秒（台詞前の間）
# situation: 深夜の電話。相手が起きているか不安で、でも繋がりを求めている。
# subtext: 返事が怖いが、繋がりを求めてしまう。
"""


def cmd_init(args) -> None:
    os.makedirs(config.PERFORMANCES_DIR, exist_ok=True)
    path = os.path.join(config.PERFORMANCES_DIR, args.name + ".direction.yaml")
    if os.path.exists(path):
        print(f"既に存在します: {path}（上書きしません）")
        return
    with open(path, "w", encoding="utf-8") as f:
        f.write(_TEMPLATE.format(name=args.name))
    print(f"作成しました: {path}")
    print("内容を編集したら `bin/performance.py validate %s` で検証してください。" % args.name)


def cmd_validate(args) -> None:
    direction = load_direction(performance_path(args.name))
    validate.validate_performance_asset(direction)
    print(f"OK: {args.name}")


def cmd_list(args) -> None:
    names = list_performances()
    if not names:
        print("（演技なし）")
        return
    for n in names:
        print(n)


def main() -> None:
    p = argparse.ArgumentParser(description="演技の振り付けを定義・検証・一覧する。")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="テンプレートを performances/ に作成")
    p_init.add_argument("name")
    p_init.set_defaults(func=cmd_init)

    p_val = sub.add_parser("validate", help="スキーマ検証")
    p_val.add_argument("name")
    p_val.set_defaults(func=cmd_validate)

    p_list = sub.add_parser("list", help="登録済み演技一覧")
    p_list.set_defaults(func=cmd_list)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
