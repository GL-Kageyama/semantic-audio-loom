"""reference Skill（参照音声ライブラリの拡充と解決を担う糊）。

参照音声（経路A の timbre 複製元）はライブラリ（config.REFERENCE_LIB）に .wav と
manifest.json（出典・ライセンス記録）で管理する。足りない声は bin/reference.py で拡充：
- synthesize: ローカル生成（Tsukasa 経路B・参照不要）で作る
- add: 著作権フリー音源（VCTK CC BY 4.0 / Common Voice CC0 など）の .wav を登録する

出典・ライセンスを manifest.json に必ず記録する（配布時に帰属表示が必要な音源があるため）。
"""
from __future__ import annotations

import json
import os

from semantic_audio_loom import config


def manifest_path() -> str:
    return os.path.join(config.REFERENCE_LIB, "manifest.json")


def load_manifest() -> dict:
    p = manifest_path()
    if not os.path.exists(p):
        return {}
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save_manifest(m: dict) -> None:
    os.makedirs(config.REFERENCE_LIB, exist_ok=True)
    with open(manifest_path(), "w", encoding="utf-8") as f:
        json.dump(m, f, ensure_ascii=False, indent=2)


def resolve_reference(ref: str) -> str | None:
    """参照音声の指定（パス or 話者キー）を実ファイルパスへ解決。見つからなければ None。

    Provider（tsukasa）の _resolve_reference と同じ解決規則。見つからない場合に
    generate.py が拡充（bin/reference.py）を案内するために使う。
    """
    if os.path.exists(ref):
        return ref
    for cand in (
        os.path.join(config.REFERENCE_LIB, ref + ".wav"),
        os.path.join(config.REFERENCE_LIB, "cloned", ref + "_clone.wav"),
    ):
        if os.path.exists(cand):
            return cand
    return None


def list_keys() -> list[str]:
    """登録済みの参照音声キー（実ファイルが存在するもの）を返す。"""
    m = load_manifest()
    return sorted(k for k in m if resolve_reference(k))


def register(key: str, wav_path: str, entry: dict) -> str:
    """ライブラリに .wav を <key>.wav として保存し、manifest.json に出典を記録する。

    entry は {age, gender, source, license, ...}（manifest.json と同じ形）。
    """
    import shutil

    os.makedirs(config.REFERENCE_LIB, exist_ok=True)
    dst = os.path.join(config.REFERENCE_LIB, key + ".wav")
    shutil.copyfile(wav_path, dst)
    m = load_manifest()
    m[key] = entry
    save_manifest(m)
    return dst
