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

# Reusable asset library (library/<type>/<name>.asset.yaml + .wav)。参照音声・
# キャラ・演技と同じ「再利用する資材」の側。生成物そのもの（projects/*/assets/）とは分ける。
LIBRARY_DIR = os.environ.get(
    "SAL_LIBRARY_DIR",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "library"),
)

# 生成物の置き場（projects/<project>/assets/...）。
PROJECTS_DIR = os.environ.get(
    "SAL_PROJECTS_DIR",
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "projects"),
)


def project_dir(project: str) -> str:
    """project 名 → プロジェクトのディレクトリ（assets/ と sound-bible.yaml の親）。"""
    return os.path.join(PROJECTS_DIR, project)

# Sampling rate Tsukasa outputs (and the loom normalizes voice to).
SAMPLE_RATE = 24000

# 保存形式（asset_type 別）＝ (sample_rate, channels)。channels が None なら
# Provider の出力チャンネル数を保つ（音楽・環境音のステレオを潰さない）。
# 声だけは Time-domain の既存契約（24kHz mono）を変えない。
OUTPUT_FORMATS = {
    "voice": (SAMPLE_RATE, 1),
    "bgm": (44100, None),
    "ambience": (44100, None),
    "sfx": (44100, None),
    "foley": (44100, None),
}

# Generation knobs (M0 実測で確定). alpha=低ほど参照 timbre 保持、beta=低ほど
# プロンプト由来の口調（演技）成分が増える。beta は「ピッチ演技のノブ」。
# 環境変数で振れる（同じ台詞を別のノブで作って比べる測定用）。生成した params.yaml には
# 実際に使った値が入るので、再生成の照合は崩れない。
ALPHA = float(os.environ.get("SAL_ALPHA", "0.35"))
BETA = float(os.environ.get("SAL_BETA", "0.7"))
