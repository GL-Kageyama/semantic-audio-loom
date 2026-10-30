"""中心オブジェクト（深掘り②スキーマに対応する実行時の実体）。

GenerationIntent が Direction（人間が書く意図）を、GenerationRequest が
Resolve 済みの Performance Spec（俳優＝実現）を内包する。
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

# 構想 §4 の正典 5 Asset Type（docs/asset-types.md 参照）。
# voice は Performance Spec、bgm は Music Spec、ambience/sfx/foley は Sound Spec を持つ。
ASSET_TYPES = ("voice", "bgm", "ambience", "sfx", "foley")
SOUND_TYPES = ("bgm", "ambience", "sfx", "foley")


@dataclass
class GenerationIntent:
    """Skill が組み立てる。asset_type は ASSET_TYPES の正典値。

    voice は voice_profile / emotion / performance / dialogue を使う。
    bgm・ambience・sfx・foley は sound dict に意味フィールドを入れる（type 別）。
    共通の scene / situation / seed は全 type が使う。
    """

    asset_type: str = "voice"

    # voice（Performance Direction）
    voice_profile: dict = field(default_factory=dict)
    character_state: dict = field(default_factory=dict)
    emotion: dict = field(default_factory=dict)        # {primary, intensity}（Direction）
    performance: dict = field(default_factory=dict)    # volume/speed/pitch/breathiness/delivery
    subtext: str = ""                                  # 台詞の裏の意味（人間上書き・任意）
    dialogue: str = ""
    reading: str = ""                                  # 読み（ふりがな《》を置換した本文。無ければ空）

    # bgm / ambience / sfx / foley（Sound Direction）
    # 例: {"role": "underscore", "mood": ["lonely"], "duration": 30, "prompt": "..."}
    sound: dict = field(default_factory=dict)

    # 共通
    scene: dict = field(default_factory=dict)
    situation: str = ""
    seed: Optional[int] = None
    quality: str = "high"


@dataclass
class GenerationRequest:
    """Resolve 済み。モデル非依存（Seam の上側）。

    `spec` は type 別の解決済み Spec（voice=Performance Spec / bgm=Music Spec /
    ambience・sfx・foley=Sound Spec）。`spec["prompt"]` が Provider へ渡す
    モデル向けの実現指示になる（voice は Spec 自体を Provider が散文へ変換する）。
    """

    asset_type: str
    spec: dict
    seed: int
    quality: str = "high"
    voice_profile: dict = field(default_factory=dict)
    dialogue: str = ""
    reading: str = ""
    duration: Optional[float] = None
    provider_hint: Optional[str] = None

    @property
    def performance_spec(self) -> dict:
        """後方互換（voice の Spec は performance_spec とも呼ぶ）。"""
        return self.spec


@dataclass
class Audio:
    """生の音声。wav は float32（-1.0〜1.0）。mono は 1 次元 `(n,)`、
    多チャンネルは `(n, channels)`（voice は mono 固定、音の 4 種は生成のチャンネル数）。"""

    wav: Any
    sample_rate: int = 24000


@dataclass
class AudioAsset:
    """Audio + Metadata + Parameters の保存単位。"""

    audio: Audio
    metadata: dict
    parameters: dict
    path: Optional[str] = None


@dataclass
class SceneCue:
    """Scene（タイムライン）内の 1 つの発話。

    character は名前で参照し（characters/<name>.voice.yaml）、voice の 7 段フロー
    そのもので生成する。pause_before は「このキューの前に入れる無音（秒）」＝間
    （余白）。間はタイムライン（mixer）の関心事なので voice の build_intent には渡さない。
    """

    character: str
    line: str
    emotion: str = "neutral"
    intensity: str = "none"
    performance: dict = field(default_factory=dict)  # volume/speed/pitch/breathiness/delivery
    situation: str = ""
    subtext: str = ""
    pause_before: Optional[float] = None  # 秒。None なら Scene.default_pause を継承
    seed: Optional[int] = None
    name: str = ""


@dataclass
class Scene:
    """複数キューを無音（間）で連結する場面（タイムライン）。

    voice を組み合わせる「合成」であり、5 Asset Type の正典には加えない。
    """

    name: str = ""
    default_pause: float = 0.0  # 各キューの既定の間（秒）
    cues: list[SceneCue] = field(default_factory=list)
