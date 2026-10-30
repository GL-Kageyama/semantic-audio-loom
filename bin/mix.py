#!/usr/bin/env python
"""CLI（Mix）: 生成済みの音（声・bgm・sfx）を1本に重ねる。

生成はしない。既にある WAV を、時刻と利得と役割（bed / voice / hit）だけで束ねる。
bed（bgm・ambience）は voice が鳴っている間だけ下がる（ducking）。天井は最後に
一度だけ掛ける（重ねる途中で切ると歪みが仕様になる）。チャンネル数はステムの最大
（mono の声は両耳の真ん中へ置く）。

mix.yaml の例:

  sample_rate: 44100
  output: scene-mix
  stems:
    - {file: bgm.wav,      role: bed,   start: 0.0, gain_db: -20}
    - {file: line-01.wav,  role: voice, start: 0.5, gain_db: 0}
    - {file: door-slam.wav, role: hit,  start: 1.2, gain_db: -6}
  duck: {threshold_db: -30, depth_db: 10, attack_s: 0.02, release_s: 0.35}
  master_peak: 0.95

  bin/mix.py --file mix.yaml --out-dir /tmp/mix
"""
from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import yaml

from semantic_audio_loom import config, i18n
from semantic_audio_loom.engine import mix, normalize
from semantic_audio_loom.engine.store import save as store_save
from semantic_audio_loom.skills.probe import read_wav
from semantic_audio_loom.types import Audio

ROLES = ("bed", "voice", "hit")
DEFAULT_DUCK = {"threshold_db": -30.0, "depth_db": 10.0, "attack_s": 0.02, "release_s": 0.35}


def _load_audio(path: str, sample_rate: int) -> np.ndarray:
    """WAV を読む。チャンネルは保つ（ステレオの定位を落とさない）。

    モノラルへ落としてから混ぜると、左右の相関が低い音ほど小さくなる。
    落とすのは「全体が mono」のときだけ。
    """
    arr, sr, ch, _ = read_wav(path)
    arr = np.asarray(arr, dtype=np.float32)
    if sr != sample_rate:
        arr = normalize._resample(arr, sr, sample_rate)
    return arr


def render(spec: dict, base_dir: str = ".") -> tuple[object, dict]:
    """mix.yaml の中身を音へ。生成はしない（ファイルが無ければ落ちる）。"""
    sample_rate = int(spec.get("sample_rate") or config.SAMPLE_RATE)
    stems = spec.get("stems") or []
    if not stems:
        raise SystemExit("mix: stems が空")

    tracks: list[tuple[np.ndarray, float, float, str]] = []
    for i, stem in enumerate(stems):
        role = str(stem.get("role") or "hit")
        if role not in ROLES:
            raise SystemExit(f"mix: stems[{i}].role は {ROLES} のどれか（{role!r}）")
        path = stem.get("file")
        if not path:
            raise SystemExit(f"mix: stems[{i}].file が無い")
        if not os.path.isabs(path):
            path = os.path.join(base_dir, path)
        if not os.path.exists(path):
            raise SystemExit(f"mix: ファイルが無い: {path}")
        wav = _load_audio(path, sample_rate)
        tracks.append((wav, float(stem.get("start") or 0.0),
                       float(stem.get("gain_db") if stem.get("gain_db") is not None else 0.0),
                       role))

    ends = [start + len(wav) / float(sample_rate) for wav, start, _, _ in tracks]
    total = max(ends) if ends else 0.0
    # 全体のチャンネル数はステムの最大（mono の声は両耳へ複製して置く）
    widest = max((1 if w.ndim == 1 else w.shape[1]) for w, *_ in tracks)
    channels = int(spec.get("channels") or widest)

    def bus(role: str):
        picked = [(w, s, g) for w, s, g, r in tracks if r == role]
        n = int(round(total * sample_rate))
        if not picked:
            return np.zeros((n, channels) if channels > 1 else n, dtype=np.float32)
        return np.asarray(mix.overlay(picked, sample_rate, total_seconds=total,
                                      channels=channels).wav)

    voice = bus("voice")
    bed = bus("bed")
    hits = bus("hit")

    duck_cfg = {**DEFAULT_DUCK, **(spec.get("duck") or {})}
    ducked = bool(duck_cfg.pop("enabled", True)) and bool(np.any(bed))
    if ducked:
        bed = mix.duck(bed, voice, sample_rate, **{k: float(v) for k, v in duck_cfg.items()})

    combined = bed + hits + voice
    audio = normalize.normalize(
        Audio(wav=combined, sample_rate=sample_rate),
        ceiling=float(spec.get("master_peak") or 0.95),
    )
    summary = {
        "sample_rate": sample_rate,
        "channels": channels,
        "duration": round(total, 3),
        "stems": len(tracks),
        "roles": {r: sum(1 for *_, role in tracks if role == r) for r in ROLES},
        "ducked": ducked,
        "duck": {k: float(v) for k, v in (spec.get("duck") or {}).items()},
    }
    return audio, summary


def main() -> None:
    lang, loc, t = i18n.translator()
    p = argparse.ArgumentParser(description=t("mix", "description", "生成済みの音を1本に重ねる。"))
    i18n.add_lang_argument(p)
    p.add_argument("--file", required=True, help=t("mix", "help_file", "mix.yaml のパス"))
    p.add_argument("--out-dir", default=".", help=t("mix", "help_out_dir", "保存先"))
    p.add_argument("--name", default=None, help=t("mix", "help_name", "出力名（既定は yaml の output）"))
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    with open(args.file, encoding="utf-8") as f:
        spec = yaml.safe_load(f) or {}
    audio, summary = render(spec, os.path.dirname(os.path.abspath(args.file)))
    name = args.name or spec.get("output") or os.path.splitext(os.path.basename(args.file))[0]
    out = store_save(
        audio,
        {"kind": "mix", **summary},
        {"file": os.path.abspath(args.file), "spec": spec},
        args.out_dir,
        name,
    )
    summary["path"] = out
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"{out}  {summary['duration']} 秒 / {summary['stems']} 本 / ducking {summary['ducked']}")


if __name__ == "__main__":
    main()
