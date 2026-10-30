"""Route（7 段フローの第 2 段）。

asset_type ごとに既定 Provider を持ち、provider_hint があればそれを優先する。
選んだ Provider の `capabilities()["asset_types"]` に asset_type が無ければ
早く失敗する（生成してから気づくより、Route で落とす）。
"""
from __future__ import annotations

from semantic_audio_loom import i18n
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


def duration_warning(
    provider: Provider, duration: float | None, lang: str | None = None
) -> str | None:
    """依頼の尺が Provider の上限を超えていたら、黙って縮めずに報せる。

    Provider は上限で切るが（MusicGen 30 秒・stub 8 秒）、切ったことを書かなければ
    依頼した尺の資材ができたように見える。返すのは文言だけで、切るのは Provider。
    """
    if not duration:
        return None
    max_seconds = provider.capabilities().get("max_seconds")
    if not max_seconds or float(duration) <= float(max_seconds):
        return None
    return i18n._t(
        i18n.load_locale(lang),
        "route",
        "duration_capped",
        "依頼した尺 {requested} 秒は {provider} の上限 {max} 秒を超えている。"
        "{max} 秒で生成する。",
        requested=f"{float(duration):g}",
        provider=provider.name,
        max=f"{float(max_seconds):g}",
    )
