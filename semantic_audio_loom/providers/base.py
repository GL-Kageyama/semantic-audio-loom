"""Provider 契約（Seam の下側の実体）。

モデル非依存の GenerationRequest を受け、自モデル API へ変換して Audio を返す。
`capabilities()` が、この Provider が何を反映できるか（controls）を宣言し、
Route / Resolve が Spec とモデル能力の整合を取る根拠にする。
"""
from __future__ import annotations

from typing import Protocol

from semantic_audio_loom.types import Audio, GenerationRequest


class Provider(Protocol):
    name: str

    def capabilities(self) -> dict:
        """この Provider が何を出せて、何を反映できるか。"""
        ...

    def generate(self, request: GenerationRequest) -> Audio:
        """モデル非依存の request を自モデル API へ変換して呼び、Audio を返す。"""
        ...
