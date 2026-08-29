"""Provider レジストリ。"""

from semantic_audio_loom.providers.tsukasa import TsukasaProvider

_PROVIDERS = {"tsukasa": TsukasaProvider()}


def get_provider(name: str):
    if name not in _PROVIDERS:
        raise ValueError(f"unknown provider: {name}")
    return _PROVIDERS[name]
