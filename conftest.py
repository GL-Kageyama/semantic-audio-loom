"""pytest の共通設定。リポジトリ直下を sys.path に加え、`semantic_audio_loom` を import 可能にする。"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
