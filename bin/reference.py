#!/usr/bin/env python
"""CLI（Step 0 — 参照音声の拡充）: 参照音声ライブラリを一覧・拡充する。

参照音声（経路A の timbre 複製元）が足りない場合、ここで拡充する：
- list: 登録済み参照音声（出典・ライセンス付き）を一覧
- synthesize: ローカル生成（Tsukasa 経路B・参照不要）。キャラの voice.yaml から
  age/gender/pitch/texture を入力して、そのキャラに合う声を生成・登録する。
- add: 著作権フリー音源（VCTK CC BY 4.0 / Common Voice CC0 など）の .wav を
  出典・ライセンス付きで登録する。

注意: synthesize（経路B）は女性バイアスが強い（男性の深い声・老人は弱い）。
性別・年齢の確実な声は `add`（著作権フリー音源の登録）が向く。

コマンド:
  bin/reference.py list
  bin/reference.py synthesize <key> --character mashiro
  bin/reference.py synthesize <key> --gender male --age elderly --pitch low --texture husky
  bin/reference.py add <wav> <key> --gender F --age 40s --license "CC BY 4.0" --source "CSTR VCTK"
"""
from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from semantic_audio_loom import config
from semantic_audio_loom.skills.character_voice import character_path, load_voice_profile
from semantic_audio_loom.skills.reference import duration_sec, load_manifest, register, synthesize_reference


def cmd_list(args) -> None:
    m = load_manifest()
    if not m:
        print("（参照音声なし）")
        return
    for k in sorted(m):
        e = m[k]
        gender = e.get("gender", "?")
        age = e.get("age", "?")
        src = e.get("source", "")
        print(f"{k:24s} {gender:>2s}  {str(age):>10s}  {src}")


def cmd_synthesize(args) -> None:
    # キャラ資材（voice.yaml）から声の属性を入力（物語上のキャラに合わせる）。
    vp = {}
    if args.character_file:
        vp = load_voice_profile(args.character_file)
    elif args.character:
        vp = load_voice_profile(character_path(args.character))

    voice = dict(vp.get("voice") or {})
    if args.age:
        voice["age"] = args.age
    if args.gender:
        voice["gender"] = args.gender
    if args.pitch:
        voice["pitch"] = args.pitch
    if args.texture:
        voice["texture"] = args.texture
    if not voice:
        print("--character（キャラ）か --gender/--age などで声の属性を指定してください。", file=sys.stderr)
        sys.exit(2)

    print(f"生成中（経路B・参照なし）… key={args.key} voice={voice}")
    dst = synthesize_reference(args.key, voice, line=args.line, seed=args.seed, provider=args.provider)
    print("登録しました:", dst)


def cmd_add(args) -> None:
    entry = {
        "age": args.age or "unknown",
        "gender": args.gender or "?",
        "duration_sec": duration_sec(args.wav),
        "source": args.source or "user-supplied",
        "license": args.license or "unspecified — 再配布前に確認必須",
        "source_files": [args.wav],
    }
    if args.source_url:
        entry["source_url"] = args.source_url
    dst = register(args.key, args.wav, entry)
    print("登録しました:", dst)
    print("※ 配布する場合は license の帰属表示（例: VCTK は CC BY 4.0）が必須です。")


def main() -> None:
    p = argparse.ArgumentParser(description="参照音声ライブラリを一覧・拡充する。")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_list = sub.add_parser("list", help="登録済み参照音声を一覧")
    p_list.set_defaults(func=cmd_list)

    p_syn = sub.add_parser("synthesize", help="ローカル生成（経路B）で参照音声を作る")
    p_syn.add_argument("key")
    p_syn.add_argument("--character", default=None, help="キャラ名（voice.yaml から声の属性を入力）")
    p_syn.add_argument("--character-file", default=None, help=".voice.yaml のパス（名前でなく直接指定）")
    p_syn.add_argument("--gender", default=None, help="female / male")
    p_syn.add_argument("--age", default=None, help="child / adolescent / young_adult / adult / middle_aged / elderly")
    p_syn.add_argument("--pitch", default=None)
    p_syn.add_argument("--texture", default=None)
    p_syn.add_argument("--line", default=None, help="参照用の台詞（既定は挨拶文）")
    p_syn.add_argument("--seed", type=int, default=None)
    p_syn.add_argument("--provider", default=None)
    p_syn.set_defaults(func=cmd_synthesize)

    p_add = sub.add_parser("add", help="著作権フリー音源の .wav を登録")
    p_add.add_argument("wav", help="登録する .wav（24kHz mono 推奨）")
    p_add.add_argument("key")
    p_add.add_argument("--gender", default=None, help="F / M")
    p_add.add_argument("--age", default=None, help="例: 18 / 40s / seventies")
    p_add.add_argument("--license", default=None, help="例: CC BY 4.0 / CC0")
    p_add.add_argument("--source", default=None, help="例: CSTR VCTK Corpus 0.92")
    p_add.add_argument("--source-url", default=None, help="取得元 URL（任意）")
    p_add.set_defaults(func=cmd_add)

    args = p.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
