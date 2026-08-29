"""Semantic Audio Loom configuration.

The Tsukasa_Speech checkout and the reference-voice library live outside this
repo (the model is ~5GB; the library carries VCTK/Common Voice licenses).
Paths are resolved here and can be overridden with environment variables.
"""
import os

# Tsukasa_Speech checkout (contains importable.py, Models/, Utils/, Configs/).
TSUKASA_DIR = os.environ.get(
    "SAL_TSUKASA_DIR",
    "/Users/user/sonic-loom-spike/tsukasa",
)

# Reference-voice library (老若男女 10 名) — 声の実体。経路A（timbre 複製元）。
# キャラ・演技資材と並ぶ再利用資材としてリポジトリ直下 references/ に置く。
# 既定は repo 直下。外部に置く場合は SAL_REFERENCE_LIB で上書きする。
REFERENCE_LIB = os.environ.get(
    "SAL_REFERENCE_LIB",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "references"),
)

# Character library — キャラ資材（再利用する Voice Profile）。声の生成とは分離し、
# ここに置いた .voice.yaml を名前で参照する。既定はリポジトリ直下の characters/。
CHARACTERS_DIR = os.environ.get(
    "SAL_CHARACTERS_DIR",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "characters"),
)

# Performance library — 演技の振り付け（再利用する Performance Direction）。
# 感情・声量・速度・delivery などの演技指示を名前で再利用する。既定は performances/。
PERFORMANCES_DIR = os.environ.get(
    "SAL_PERFORMANCES_DIR",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "performances"),
)

# Sampling rate Tsukasa outputs (and the loom normalizes to).
SAMPLE_RATE = 24000

# Generation knobs (M0 実測で確定). alpha=低ほど参照 timbre 保持、beta=低ほど
# プロンプト由来の口調（演技）成分が増える。beta は「ピッチ演技のノブ」。
ALPHA = 0.35
BETA = 0.7
