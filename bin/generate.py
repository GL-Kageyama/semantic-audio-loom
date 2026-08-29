#!/usr/bin/env python
"""CLI（Step 2 — 声の生成）: 定義済みキャラ × 台詞 × Direction → 演技付き音声。

キャラは名前で参照（Step 1 の bin/character.py で作ったキャラ資材を再利用）。
生成した音声（生成資材）は projects/<project>/assets/<scene>/ に分離して保存し、
キャラ資材（characters/）とは混ぜない。

例:
  bin/character.py init mashiro
  bin/generate.py --character mashiro --project demo --scene morning \
      --line "おはよう。今日はいい天気だね。" \
      --emotion joy --intensity moderate --speed natural --name mashiro_morning

Resolve は既定 LLM（--resolve rule で決定的写像）。subtext は --subtext で上書き可。
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml

from semantic_audio_loom.engine import AudioAssetEngine
from semantic_audio_loom.skills.character_voice import (
    build_intent,
    character_path,
    load_voice_profile,
)
from semantic_audio_loom.skills.performance import load_direction, performance_path
from semantic_audio_loom.skills.reference import resolve_reference

_PERF_KEYS = ("volume", "speed", "pitch", "breathiness", "delivery")


def main() -> None:
    p = argparse.ArgumentParser(description="Generate a voice asset.")
    p.add_argument("--character", default=None, help="キャラ名（characters/<name>.voice.yaml）")
    p.add_argument("--character-file", default=None, help=".voice.yaml のパス（名前でなく直接指定）")
    p.add_argument("--line", required=True, help="台詞（日本語）")
    p.add_argument("--performance", default=None, help="演技名（performances/<name>.direction.yaml）")
    p.add_argument("--emotion", default=None)
    p.add_argument("--intensity", default=None)
    p.add_argument("--volume")
    p.add_argument("--speed")
    p.add_argument("--pitch")
    p.add_argument("--breathiness")
    p.add_argument("--delivery")
    p.add_argument("--situation", default=None, help="状況（subtext 推論の入力）")
    p.add_argument("--state-file", default=None, help="キャラクター状態の YAML（character_state）")
    p.add_argument("--subtext", default=None, help="台詞の裏の意味（人間上書き・任意）")
    p.add_argument("--resolve", choices=("llm", "rule"), default="llm")
    p.add_argument("--project", default="demo", help="生成資材の保存先 projects/<project>/assets/")
    p.add_argument("--scene", default="default", help="生成資材の保存先サブフォルダ（シーン名）")
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--name", default=None, help="出力ファイル名（.wav/.params.yaml の接頭辞）")
    p.add_argument("--provider", default=None)
    args = p.parse_args()

    if args.character and args.character_file:
        p.error("--character と --character-file は排他です")
    if not args.character and not args.character_file:
        p.error("--character（キャラ名）か --character-file（パス）のどちらかが必要です")

    if args.character_file:
        vp = load_voice_profile(args.character_file)
    else:
        vp = load_voice_profile(character_path(args.character))

    state = {}
    if args.state_file:
        with open(args.state_file, encoding="utf-8") as f:
            state = yaml.safe_load(f) or {}

    # 演技の振り付け（演技資材）を読み、CLI フラグで上書きする（未指定は上書きしない）。
    base = {}
    if args.performance:
        base = load_direction(performance_path(args.performance))
    emotion = args.emotion if args.emotion is not None else base.get("emotion", "neutral")
    intensity = args.intensity if args.intensity is not None else base.get("intensity", "none")
    situation = args.situation if args.situation is not None else base.get("situation", "")
    subtext = args.subtext if args.subtext is not None else base.get("subtext", "")
    performance = {}
    for k in _PERF_KEYS:
        value = getattr(args, k)
        if value is not None:
            performance[k] = value
        elif k in base:
            performance[k] = base[k]

    # 参照音声が足りない場合、拡充を案内する（既定で常に検査）。
    ref = vp.get("reference_audio") or (vp.get("voice") or {}).get("reference_audio")
    if ref and resolve_reference(ref) is None:
        who = args.character or args.character_file or "<name>"
        print(f"⚠️  参照音声が見つかりません: {ref}", file=sys.stderr)
        print(f"   拡充: bin/reference.py synthesize <key> --character {who}", file=sys.stderr)
        print("   または bin/reference.py add <wav> <key>（著作権フリー音源を登録）", file=sys.stderr)

    intent = build_intent(
        vp, args.line, emotion, intensity, performance,
        situation=situation, state=state, subtext=subtext, seed=args.seed,
    )

    out_dir = os.path.join("projects", args.project, "assets", args.scene)
    engine = AudioAssetEngine(provider_name=args.provider, resolve_mode=args.resolve)
    asset = engine.generate(intent, out_dir=out_dir, name=args.name)

    print("wav:", asset.path)
    print("seed:", asset.parameters["seed"])
    print("spec:", json.dumps(asset.parameters["performance_spec"], ensure_ascii=False))
    print("metadata:", json.dumps(asset.metadata, ensure_ascii=False))


if __name__ == "__main__":
    main()
