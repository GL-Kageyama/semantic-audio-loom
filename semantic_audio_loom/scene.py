"""Scene（場面＝複数 voice キューの合成）の読み込みと再構成。

scene.yaml（宣言的な源）を `Scene` へ読み込み、保存済み scene.params.yaml の
per-cue パラメータから `GenerationRequest` を再構成する（再生成用）。合成そのものは
`semantic_audio_loom/engine/mix.py`、検証は `engine/validate.py` の `validate_scene`。
"""
from __future__ import annotations

from semantic_audio_loom.types import GenerationRequest, Scene, SceneCue

# SceneCue が Direction（volume/speed/pitch/breathiness/delivery）を performance dict に
# 畳む際のキー。bin/generate.py の _PERF_KEYS と同じ集合。
DIRECTION_KEYS = ("volume", "speed", "pitch", "breathiness", "delivery")


def load_scene(path: str) -> Scene:
    """scene.yaml を読み、flat な Direction キーを performance dict へ畳んで Scene を返す。"""
    import yaml

    with open(path, encoding="utf-8") as f:
        doc = yaml.safe_load(f) or {}

    scene = Scene(
        name=doc.get("name", ""),
        default_pause=float(doc.get("default_pause", 0.0)),
    )
    for cue_doc in doc.get("cues", []):
        cue_doc = cue_doc or {}
        performance = {k: cue_doc[k] for k in DIRECTION_KEYS if k in cue_doc}
        scene.cues.append(
            SceneCue(
                character=cue_doc.get("character", ""),
                line=cue_doc.get("line", ""),
                emotion=cue_doc.get("emotion", "neutral"),
                intensity=cue_doc.get("intensity", "none"),
                performance=performance,
                situation=cue_doc.get("situation", ""),
                subtext=cue_doc.get("subtext", ""),
                pause_before=cue_doc.get("pause_before"),
                seed=cue_doc.get("seed"),
                name=cue_doc.get("name", ""),
            )
        )
    return scene


def cue_from_params(cue: dict) -> GenerationRequest:
    """保存済み per-cue params（voice params + pause_before/name）から GenerationRequest を再構成。

    bin/regenerate.py と同じ再現経路（LLM を再呼び出ししない）。voice_profile・
    performance_spec・dialogue・reading・seed は params に完全写しされている。
    """
    return GenerationRequest(
        asset_type="voice",
        voice_profile=cue["voice_profile"],
        spec=cue["performance_spec"],
        dialogue=cue["dialogue"],
        reading=cue.get("reading", ""),
        seed=cue["seed"],
        quality="high",
        provider_hint=cue.get("provider"),
    )
