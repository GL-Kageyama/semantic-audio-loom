"""library Skill — 再利用する音響資材の管理（生成＋ライブラリの「ライブラリ」側）。

生成物（projects/*/assets/）は使い捨て、ライブラリ（library/）は再利用する。
1 つの資材は WAV と `<name>.asset.yaml`（意味タグ・出典・ライセンス・ループ点）の
組で持つ。検索は意味タグと Spec の語を対象にした決定的な部分一致（埋め込み不要）。

置き場は `SAL_LIBRARY_DIR`（既定はリポジトリ直下の library/）。
"""
from __future__ import annotations

import os
import shutil
import wave

import yaml

from semantic_audio_loom import config
from semantic_audio_loom.engine import validate

SUFFIX = ".asset.yaml"


def library_dir() -> str:
    return config.LIBRARY_DIR


def asset_path(asset_type: str, name: str) -> str:
    return os.path.join(library_dir(), asset_type, name + SUFFIX)


def wav_path(asset_type: str, name: str) -> str:
    return os.path.join(library_dir(), asset_type, name + ".wav")


def _wav_info(path: str) -> dict:
    try:
        with wave.open(path, "rb") as w:
            frames = w.getnframes()
            rate = w.getframerate()
            return {
                "sample_rate": rate,
                "channels": w.getnchannels(),
                "duration": round(frames / float(rate), 3) if rate else 0.0,
            }
    except Exception:
        return {}


def add_wav(
    src_wav: str,
    asset_type: str,
    name: str,
    spec: dict | None = None,
    semantic: dict | None = None,
    tags: list[str] | None = None,
    license: str = "",
    attribution: str = "",
    source: dict | None = None,
    loop: dict | None = None,
) -> dict:
    """WAV をライブラリへ取り込み、.asset.yaml を書く。書いたメタデータを返す。"""
    import datetime

    os.makedirs(os.path.join(library_dir(), asset_type), exist_ok=True)
    dst = wav_path(asset_type, name)
    if os.path.abspath(src_wav) != os.path.abspath(dst):
        shutil.copyfile(src_wav, dst)

    info = _wav_info(dst)
    doc = {
        "name": name,
        "asset_type": asset_type,
        "spec": spec or {},
        "semantic": semantic or {},
        "tags": list(tags or []),
        "license": license,
        "attribution": attribution,
        "source": source or {},
        "files": {"wav": os.path.basename(dst)},
        "created_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
    if loop:
        doc["loop"] = loop
    doc.update({k: v for k, v in info.items() if v is not None})
    validate.validate_library_asset(doc)

    with open(asset_path(asset_type, name), "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False)
    return doc


def add_generated(
    asset,
    asset_type: str,
    name: str,
    semantic: dict | None = None,
    tags: list[str] | None = None,
    license: str = "",
    attribution: str = "",
) -> dict:
    """生成済みの AudioAsset（engine の戻り値）をライブラリへ取り込む。

    出典（provider / model / seed / prompt）は Spec と params から写す。
    """
    spec = asset.parameters.get("spec") or asset.parameters.get("performance_spec") or {}
    loop = spec.get("loop") if isinstance(spec.get("loop"), dict) else None
    return add_wav(
        src_wav=asset.path,
        asset_type=asset_type,
        name=name,
        spec=spec,
        semantic=semantic or _default_semantic(asset_type, spec),
        tags=tags,
        license=license,
        attribution=attribution,
        source={
            "provider": asset.parameters.get("provider"),
            "seed": asset.parameters.get("seed"),
            "prompt": spec.get("prompt"),
        },
        loop=loop,
    )


def _default_semantic(asset_type: str, spec: dict) -> dict:
    """Spec から検索用の意味フィールドを抜く（空でないものだけ）。"""
    keys = {
        "bgm": ("role", "genre", "mood", "tempo", "energy"),
        "ambience": ("environment", "location", "time", "weather", "space", "mood"),
        "sfx": ("event", "object", "material", "distance", "mood"),
        "foley": ("action", "object", "surface", "contact"),
    }.get(asset_type, ())
    return {k: spec[k] for k in keys if spec.get(k)}


def list_assets(asset_type: str | None = None) -> list[dict]:
    root = library_dir()
    if not os.path.isdir(root):
        return []
    types = [asset_type] if asset_type else sorted(
        d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))
    )
    docs = []
    for t in types:
        folder = os.path.join(root, t)
        if not os.path.isdir(folder):
            continue
        for fname in sorted(os.listdir(folder)):
            if fname.endswith(SUFFIX):
                with open(os.path.join(folder, fname), encoding="utf-8") as f:
                    docs.append(yaml.safe_load(f) or {})
    return docs


def find(name: str, asset_type: str | None = None) -> dict | None:
    for doc in list_assets(asset_type):
        if doc.get("name") == name:
            return doc
    return None


def search(query: str = "", asset_type: str | None = None, tags: list[str] | None = None) -> list[dict]:
    """意味フィールド・タグ・プロンプトの部分一致で探す（一致数の多い順）。

    埋め込み検索ではなく決定的な語の照合。query は空白・カンマ区切りの語。
    """
    tokens = [t for t in _split(query) if t]
    wanted = set(tags or [])
    scored = []
    for doc in list_assets(asset_type):
        haystack = _haystack(doc)
        doc_tags = set(doc.get("tags") or [])
        if wanted and not wanted.issubset(doc_tags):
            continue
        score = sum(1 for tok in tokens if tok in haystack)
        if tokens and score == 0:
            continue
        scored.append((score, doc.get("name") or "", doc))
    scored.sort(key=lambda x: (-x[0], x[1]))
    return [doc for _, _, doc in scored]


def _split(text: str) -> list[str]:
    out = []
    for chunk in (text or "").replace("、", ",").split(","):
        out.extend(chunk.split())
    return [t.strip().lower() for t in out]


def _haystack(doc: dict) -> str:
    parts = [doc.get("name") or ""]
    parts.extend(doc.get("tags") or [])
    semantic = doc.get("semantic") or {}
    for value in semantic.values():
        parts.extend(value if isinstance(value, list) else [str(value)])
    spec = doc.get("spec") or {}
    for key in ("prompt", "role", "kind", "environment", "event", "action", "object", "mood"):
        value = spec.get(key)
        if isinstance(value, list):
            parts.extend(str(v) for v in value)
        elif value:
            parts.append(str(value))
    return " ".join(parts).lower()


def validate_all() -> list[str]:
    """ライブラリ全体を検証する。問題のメッセージ一覧を返す（空なら健全）。"""
    problems = []
    for doc in list_assets():
        name = doc.get("name") or "?"
        try:
            validate.validate_library_asset(doc)
        except Exception as exc:
            problems.append(f"{name}: {exc}")
            continue
        wav = os.path.join(library_dir(), doc.get("asset_type", ""), doc["files"]["wav"])
        if not os.path.exists(wav):
            problems.append(f"{name}: missing wav {wav}")
    return problems
