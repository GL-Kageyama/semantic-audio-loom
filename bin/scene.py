#!/usr/bin/env python
"""CLI（Scene / Timeline）: 複数人物の台詞を「間（無音）」で連結し、1 WAV に合成する。

scene.yaml がキュー（キャラ＋台詞＋Direction＋pause_before）を宣言し、各キューを
既存の voice 生成（bin/generate.py と同じ 7 段フロー）で生成してから連結する。
voice の生成ループは一切変えない（合成レイヤとして外側に置く）。

例:
  bin/scene.py --scene-file examples/gozen-niji-ch01/scene.yaml --project gozen-niji
  bin/scene.py --params examples/gozen-niji-ch01/gozen-niji-ch01.params.yaml --out-dir /tmp/regen

再生成（--params）は保存済み Spec を再利用し、LLM を再呼び出ししない（seed決定論）。
"""
from __future__ import annotations

import argparse
import datetime
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import yaml

from semantic_audio_loom import config, i18n
from semantic_audio_loom.engine import AudioAssetEngine, mix, normalize
from semantic_audio_loom.engine.store import save as store_save
from semantic_audio_loom.engine.validate import validate_scene
from semantic_audio_loom.scene import cue_from_params, load_scene
from semantic_audio_loom.skills.character_voice import (
    build_intent,
    character_path,
    load_voice_profile,
)
from semantic_audio_loom.types import Audio


def _scene_metadata(base: str, cue_count: int, audio: Audio) -> dict:
    return {
        "kind": "scene",
        "name": base,
        "cue_count": cue_count,
        "sample_rate": audio.sample_rate,
        "duration_sec": round(float(len(audio.wav)) / audio.sample_rate, 3),
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }


def _save_scene(
    audio: Audio,
    base: str,
    parameters: dict,
    out_dir: str,
) -> str:
    metadata = _scene_metadata(base, len(parameters["cues"]), audio)
    return store_save(audio, metadata, parameters, out_dir, base)


def _render(args, lang: str) -> None:
    scene = load_scene(args.scene_file)
    validate_scene(scene)

    stem = os.path.splitext(os.path.basename(args.scene_file))[0]
    base = args.name or scene.name or stem

    engine = AudioAssetEngine(provider_name=args.provider, resolve_mode=args.resolve, lang=lang)

    cues_for_mix: list[tuple] = []
    cue_params_list: list[dict] = []
    for i, cue in enumerate(scene.cues):
        vp = load_voice_profile(character_path(cue.character))
        seed = cue.seed if cue.seed is not None else random.randint(0, 2**31 - 1)
        intent = build_intent(
            vp, cue.line, cue.emotion, cue.intensity, cue.performance,
            situation=cue.situation, subtext=cue.subtext, seed=seed,
        )
        # 個別保存せず（out_dir なし）メモリ上で合成する。Provider（Tsukasa）は
        # 同一プロセスで保持され、1 回だけロードされる。
        asset = engine.generate(intent)
        pause = cue.pause_before if cue.pause_before is not None else scene.default_pause
        cues_for_mix.append((asset.audio.wav, pause))

        cue_params = dict(asset.parameters)
        cue_params["pause_before"] = pause
        cue_params["name"] = cue.name or f"cue_{i:02d}"
        cue_params["character"] = cue.character
        cue_params_list.append(cue_params)

    audio = normalize.normalize(mix.mix_cues(cues_for_mix, config.SAMPLE_RATE))
    parameters = {
        "version": 1,
        "sample_rate": config.SAMPLE_RATE,
        "default_pause": scene.default_pause,
        "cues": cue_params_list,
    }
    out_dir = os.path.join("projects", args.project, "assets", base)
    path = _save_scene(audio, base, parameters, out_dir)

    print("wav:", path)
    print("cues:", len(cue_params_list))


def _regen(args) -> None:
    with open(args.params, encoding="utf-8") as f:
        doc = yaml.safe_load(f)
    params = doc["parameters"]
    name = args.name or doc.get("name") or os.path.splitext(os.path.basename(args.params))[0]

    engine = AudioAssetEngine()

    cues_for_mix: list[tuple] = []
    for cue in params["cues"]:
        asset = engine.generate_request(cue_from_params(cue))
        cues_for_mix.append((asset.audio.wav, cue.get("pause_before", 0.0)))

    audio = normalize.normalize(mix.mix_cues(cues_for_mix, config.SAMPLE_RATE))
    path = _save_scene(audio, name, params, args.out_dir)

    print("wav:", path)
    print("cues:", len(params["cues"]))


def main() -> None:
    lang, _loc, t = i18n.translator()
    p = argparse.ArgumentParser(description=t("scene", "description", "複数人物の台詞を 1 つの WAV に合成する。"))
    i18n.add_lang_argument(p)
    p.add_argument("--scene-file", default=None, help=t("scene", "help_scene_file", "scene.yaml のパス（キャラ＋台詞＋Direction＋間）"))
    p.add_argument("--params", default=None, help=t("scene", "help_params", "保存済み scene.params.yaml のパス（再生成・LLM なし）"))
    p.add_argument("--project", default="demo", help=t("scene", "help_project", "保存先 projects/<project>/assets/<scene>/"))
    p.add_argument("--name", default=None, help=t("scene", "help_name", "出力名（.wav/.params.yaml の接頭辞）"))
    p.add_argument("--resolve", choices=("llm", "rule"), default="llm")
    p.add_argument("--provider", default=None)
    p.add_argument("--out-dir", default="output_scene_regen", help=t("scene", "help_out_dir", "--params 再生成時の保存先ディレクトリ"))
    args = p.parse_args()

    if bool(args.scene_file) == bool(args.params):
        p.error(t("scene", "err_need_source", "--scene-file か --params のどちらか一方が必要です"))

    if args.scene_file:
        _render(args, lang)
    else:
        _regen(args)


if __name__ == "__main__":
    main()
