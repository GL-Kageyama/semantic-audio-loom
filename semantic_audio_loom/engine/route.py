"""Route（7 段フローの第 2 段）。

asset_type ごとに既定 Provider を持ち、provider_hint があればそれを優先する。
選んだ Provider の `capabilities()["asset_types"]` に asset_type が無ければ
早く失敗する（生成してから気づくより、Route で落とす）。
"""
from __future__ import annotations

from semantic_audio_loom.providers import get_provider
from semantic_audio_loom.providers.base import Provider

DEFAULTS = {
    "voice": "tsukasa",
    "bgm": "musicgen",
    "ambience": "stable_audio",
    "sfx": "stable_audio",
    "foley": "stable_audio",
}


def route(asset_type: str = "voice", provider_hint: str | None = None) -> Provider:
    name = provider_hint or DEFAULTS.get(asset_type)
    if not name:
        raise ValueError(f"no default provider for asset_type: {asset_type!r}")
    provider = get_provider(name)
    supported = provider.capabilities().get("asset_types", [])
    if asset_type not in supported:
        raise ValueError(
            f"provider {name!r} cannot generate {asset_type!r} "
            f"(supports: {', '.join(supported)})"
        )
    return provider
