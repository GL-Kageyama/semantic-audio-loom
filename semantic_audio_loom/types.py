"""中心オブジェクト（深掘り②スキーマに対応する実行時の実体）。

GenerationIntent が Direction（人間が書く意図）を、GenerationRequest が
Resolve 済みの Performance Spec（俳優＝実現）を内包する。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional


@dataclass
class GenerationIntent:
    """Skill が組み立てる。asset_type で分岐する（M1 は voice のみ）。"""

    asset_type: str = "voice"
    voice_profile: dict = field(default_factory=dict)
    scene: dict = field(default_factory=dict)
    situation: str = ""
    character_state: dict = field(default_factory=dict)
    emotion: dict = field(default_factory=dict)        # {primary, intensity}（Direction）
    performance: dict = field(default_factory=dict)    # Direction: volume/speed/pitch/breathiness/delivery
    subtext: str = ""                                  # 台詞の裏の意味（人間上書き・任意）
    dialogue: str = ""
    seed: Optional[int] = None
    quality: str = "high"


@dataclass
class GenerationRequest:
    """Resolve 済み（performance_spec を内包）。モデル非依存。"""

    asset_type: str
    voice_profile: dict
    performance_spec: dict
    dialogue: str
    seed: int
    quality: str
    provider_hint: Optional[str] = None


@dataclass
class Audio:
    """生の音声。wav は float32 の mono 波形（-1.0〜1.0）。"""

    wav: Any
    sample_rate: int = 24000


@dataclass
class AudioAsset:
    """Audio + Metadata + Parameters の保存単位。"""

    audio: Audio
    metadata: dict
    parameters: dict
    path: Optional[str] = None
