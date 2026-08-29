"""Route（7 段フローの第 2 段）。

M2 では Provider は Tsukasa のみ。provider_hint があればそれを使い、
なければ既定へ落とす。M3 以降は voice_profile の要請（言語・性別・一貫性）と
Provider の capabilities() を突き合わせて選ぶ。
"""
from __future__ import annotations

from semantic_audio_loom.providers import get_provider
from semantic_audio_loom.providers.base import Provider

_DEFAULT = "tsukasa"


def route(provider_hint: str | None = None) -> Provider:
    return get_provider(provider_hint or _DEFAULT)
