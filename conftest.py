"""pytest の共通設定。

- リポジトリ直下を sys.path に加え、`semantic_audio_loom` を import 可能にする。
- `SAL_LANG` を既定 `ja` に固定（既定は ja だが、将来の既定変更からテストを守る）。
- 各テストで i18n キャッシュを破棄し、言語差のリークを防ぐ。
- LLM はモックするため、`ANTHROPIC_API_KEY` を差し込む（ClaudeClient の認証チェックを通す）。
"""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("SAL_LANG", "ja")


@pytest.fixture(autouse=True)
def _api_key(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")


@pytest.fixture(autouse=True)
def _clear_i18n_cache():
    from semantic_audio_loom import i18n

    i18n.clear_cache()
    yield
    i18n.clear_cache()
