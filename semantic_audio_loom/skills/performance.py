"""performance Skill（演技の振り付けの再利用を担う糊）。

.direction.yaml（performance_asset.schema.json 準拠）を読み、Direction の素にする。
感情・声量・速度・delivery などの演技指示と、状況（situation）・裏の意味（subtext）を
名前で再利用する。声の生成（bin/generate.py --performance <name>）が参照する。

キャラ資材（characters/）が「誰の声か」を再利用するのに対し、演技資材
（performances/）は「どう演じるか」を再利用する。両者を組み合わせて台詞ごとに
声を生成する。
"""
from __future__ import annotations

import os

from semantic_audio_loom import config


def load_direction(path: str) -> dict:
    import yaml

    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def performance_path(name: str) -> str:
    """演技名 → performances/<name>.direction.yaml のパス（拡張子は補完可）。"""
    if name.endswith((".yaml", ".yml")):
        name = name.rsplit(".", 1)[0]
    path = os.path.join(config.PERFORMANCES_DIR, name + ".direction.yaml")
    if not os.path.exists(path):
        raise FileNotFoundError(
            f"演技 '{name}' が見つかりません: {path}（bin/performance.py init {name} で作成）"
        )
    return path


def list_performances() -> list[str]:
    """performances/ にある演技名（.direction.yaml の接頭辞）を返す。"""
    if not os.path.isdir(config.PERFORMANCES_DIR):
        return []
    names = []
    for fname in sorted(os.listdir(config.PERFORMANCES_DIR)):
        if fname.endswith(".direction.yaml"):
            names.append(fname[: -len(".direction.yaml")])
    return names
