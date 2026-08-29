#!/usr/bin/env python
"""CLI（蒸留）: 大量のインプット（物語・脚本・人物描写）から再利用資材を蒸留する。

手で埋める資材（character.py init / performance.py init）の代わりに、テキストから
キャラ（voice_profile）と演技（performance_asset）を自動生成する。distill-essence-engine の
蒸留（①理解→②選択→③翻訳）を音声資材向けに翻案。

二モード：
  batch       … 物語テキスト1つ → 主要キャラ複数 × 代表シーン複数
  character   … 1入力 → キャラ1体（--name 必須）
  performance … 1入力 → 演技1つ（--name 必須）

入力は位置引数（テキスト）か --file。--synthesize でキャラの元音声も経路B生成・登録。

例:
  bin/distill.py batch story.txt
  bin/distill.py batch --file story.txt --synthesize --dry-run
  bin/distill.py character "金髪で低い声の青年" --name rei
  bin/distill.py performance "深夜、返事が怖い電話" --name anxious-call
"""
from __future__ import annotations

import argparse
import os
import sys

import yaml

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from semantic_audio_loom import i18n
from semantic_audio_loom.engine import distill
from semantic_audio_loom.skills.reference import synthesize_reference


def _read_input(args) -> str:
    if args.file:
        with open(args.file, encoding="utf-8") as f:
            return f.read()
    if args.input:
        return args.input
    print(args.t("distill", "err_need_input", "テキスト（位置引数）か --file のどちらかが必要です。"), file=sys.stderr)
    sys.exit(2)


def _add_common(p, t) -> None:
    p.add_argument("input", nargs="?", default=None, help=t("distill", "help_input", "入力テキスト（--file がない場合）"))
    p.add_argument("--file", default=None, help=t("distill", "help_file", "入力ファイル（テキスト）"))


def _add_character_flags(p, t) -> None:
    p.add_argument("--synthesize", action="store_true", help=t("distill", "help_synthesize", "キャラの元音声も経路Bで生成・登録"))
    p.add_argument("--provider", default=None)
    _add_write_flags(p, t)


def _add_write_flags(p, t) -> None:
    p.add_argument("--overwrite", action="store_true", help=t("distill", "help_overwrite", "既存の同名資材を上書き"))
    p.add_argument("--dry-run", action="store_true", help=t("distill", "help_dry_run", "書き出さず YAML を表示のみ"))


def _dump_character(name: str, character: str, voice: dict, reference_audio: str | None = None) -> str:
    profile = {"character": character or name, "voice": voice}
    if reference_audio:
        profile["reference_audio"] = reference_audio
    return yaml.safe_dump(profile, allow_unicode=True, sort_keys=False, default_flow_style=False)


def _dump_performance(fields: dict) -> str:
    return yaml.safe_dump(fields, allow_unicode=True, sort_keys=False, default_flow_style=False)


def _write_character_asset(name: str, character: str, voice: dict, args) -> None:
    """キャラ1体を書き出す（--synthesize / --dry-run / --overwrite を反映）。"""
    if args.dry_run:
        print(args.t("distill", "char_header", "# キャラ: {name} ({character})", name=name, character=character))
        print(_dump_character(name, character, voice))
        return
    ref_key = None
    if args.synthesize:
        print(args.t("distill", "synthesizing_voice", "元音声を生成中… {name}", name=name))
        synthesize_reference(name, voice, provider=getattr(args, "provider", None))
        ref_key = name
    asset = {"name": name, "character": character, "voice": voice}
    if ref_key:
        asset["reference_audio"] = ref_key
    try:
        path = distill.write_character(asset, overwrite=args.overwrite, lang=args.lang)
        print(args.t("distill", "wrote", "書きました: {path}", path=path))
    except FileExistsError as e:
        print(args.t("distill", "skipped", "スキップ: {e}", e=e), file=sys.stderr)


def cmd_batch(args) -> None:
    text = _read_input(args)
    characters = distill.distill_characters(text, lang=args.lang)
    performances = distill.distill_performances(text, lang=args.lang)
    print(args.t("distill", "result_summary", "蒸留結果: キャラ {n_chars} 人 / 演技 {n_perfs} つ", n_chars=len(characters), n_perfs=len(performances)) + "\n")

    for c in characters:
        name = distill.slug(c.get("name") or "")
        character = c.get("character") or name
        voice = {k: v for k, v in (c.get("voice") or {}).items() if v}
        _write_character_asset(name, character, voice, args)

    for p in performances:
        name = distill.slug(p.get("name") or "")
        fields = {k: v for k, v in p.items() if k != "name" and v not in (None, "")}
        if args.dry_run:
            print(args.t("distill", "perf_header", "# 演技: {name}", name=name))
            print(_dump_performance(fields))
            continue
        asset = dict(p)
        asset["name"] = name
        try:
            path = distill.write_performance(asset, overwrite=args.overwrite, lang=args.lang)
            print(args.t("distill", "wrote", "書きました: {path}", path=path))
        except FileExistsError as e:
            print(args.t("distill", "skipped", "スキップ: {e}", e=e), file=sys.stderr)


def cmd_character(args) -> None:
    text = _read_input(args)
    data = distill.distill_character(text, lang=args.lang)
    name = distill.slug(args.name)
    character = data.get("character") or name
    voice = {k: v for k, v in (data.get("voice") or {}).items() if v}
    _write_character_asset(name, character, voice, args)


def cmd_performance(args) -> None:
    text = _read_input(args)
    data = distill.distill_performance(text, lang=args.lang)
    name = distill.slug(args.name)
    fields = {k: v for k, v in data.items() if v not in (None, "")}
    if args.dry_run:
        print(args.t("distill", "perf_header", "# 演技: {name}", name=name))
        print(_dump_performance(fields))
        return
    asset = dict(data)
    asset["name"] = name
    try:
        path = distill.write_performance(asset, overwrite=args.overwrite, lang=args.lang)
        print(args.t("distill", "wrote", "書きました: {path}", path=path))
    except FileExistsError as e:
        print(args.t("distill", "skipped", "スキップ: {e}", e=e), file=sys.stderr)


def main() -> None:
    lang, loc, t = i18n.translator()
    p = argparse.ArgumentParser(description=t("distill", "description", "大量のインプットから音声資材（キャラ・演技）を蒸留する。"))
    i18n.add_lang_argument(p)
    sub = p.add_subparsers(dest="cmd", required=True)

    pb = sub.add_parser("batch", help=t("distill", "help_batch", "物語テキスト1つ → 主要キャラ複数 × 代表シーン複数"))
    _add_common(pb, t)
    _add_character_flags(pb, t)
    pb.set_defaults(func=cmd_batch)

    pc = sub.add_parser("character", help=t("distill", "help_character", "1入力 → キャラ1体"))
    _add_common(pc, t)
    pc.add_argument("--name", required=True, help=t("distill", "help_name_char", "キャラ名（スラッグ）"))
    _add_character_flags(pc, t)
    pc.set_defaults(func=cmd_character)

    pp = sub.add_parser("performance", help=t("distill", "help_performance", "1入力 → 演技1つ"))
    _add_common(pp, t)
    pp.add_argument("--name", required=True, help=t("distill", "help_name_perf", "演技名（スラッグ）"))
    _add_write_flags(pp, t)
    pp.set_defaults(func=cmd_performance)

    args = p.parse_args()
    args.lang, args.loc, args.t = lang, loc, t
    args.func(args)


if __name__ == "__main__":
    main()
