"""Provider レジストリ。

重い依存（torch・transformers・diffusers）を持つ Provider は、名前を引かれた
時点で初めて import する。`semantic_audio_loom` の import だけで 5GB の
チェックポイントに触らないため。
"""
from __future__ import annotations

_FACTORIES = {
    "tsukasa": "semantic_audio_loom.providers.tsukasa:TsukasaProvider",
    "musicgen": "semantic_audio_loom.providers.musicgen:MusicGenProvider",
    "stable_audio": "semantic_audio_loom.providers.stable_audio:StableAudioProvider",
    "stub": "semantic_audio_loom.providers.stub:StubProvider",
}

_INSTANCES: dict = {}


def available() -> list[str]:
    return sorted(_FACTORIES)


def get_provider(name: str):
    if name in _INSTANCES:
        return _INSTANCES[name]
    target = _FACTORIES.get(name)
    if target is None:
        raise ValueError(f"unknown provider: {name} (known: {', '.join(available())})")

    import importlib

    module_name, class_name = target.split(":")
    module = importlib.import_module(module_name)
    instance = getattr(module, class_name)()
    _INSTANCES[name] = instance
    return instance
