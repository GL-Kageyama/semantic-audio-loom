"""言語解決とロケール/プロンプト読み込み（en/ja/zh）。

並列リポジトリ（wisdom-council-layer / elevate-draft-engine）の 3層方式のうち、
SAL では 2層だけを実装する（docs ミラーツリーは省略。README/CLAUDE/docs は日本語のまま）。

- `locales/{lang}.json` … CLI / UI 文字列（help・print・エラー・YAML テンプレート）
- `prompts/{lang}.json` … LLM プロンプト（resolve・distill）

言語選択の優先順位（3段）:
1. CLI フラグ `--lang {en,ja,zh}`
2. 環境変数 `SAL_LANG`
3. デフォルト `ja`（日本語 TTS・日本語ユーザー中心のため日本語中心を維持）

規約:
- 固定列挙値（enum）は全言語で英語のまま。自由テキスト（situation/subtext/表示名）は
  `--lang` の言語で出力する（各プロンプト末尾の出力言語ディレクティブで保証）。
- 台詞（`--line`）は日本語のまま（Tsukasa が日本語 TTS のため。領域事実＝i18n 対象外）。
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

_SUPPORTED = ("en", "ja", "zh")
_ENV_VAR = "SAL_LANG"
_DEFAULT_LANG = "ja"

_cache: dict[str, dict[str, dict]] = {"locales": {}, "prompts": {}}


def resolve_lang(cli_lang: str | None = None) -> str:
    """--lang フラグ > SAL_LANG 環境変数 > 既定 ja。未対応言語は警告して ja へ。"""
    lang = (cli_lang or os.environ.get(_ENV_VAR) or _DEFAULT_LANG).lower()
    if lang not in _SUPPORTED:
        sys.stderr.write(
            f"[i18n] 未対応の言語 '{lang}' は使えません。'{_DEFAULT_LANG}' にフォールバックします。\n"
        )
        return _DEFAULT_LANG
    return lang


def _load(kind: str, lang: str | None) -> dict:
    resolved = resolve_lang(lang)
    if resolved not in _cache[kind]:
        path = Path(__file__).resolve().parent.parent / kind / f"{resolved}.json"
        _cache[kind][resolved] = json.loads(path.read_text(encoding="utf-8"))
    return _cache[kind][resolved]


def load_locale(lang: str | None = None) -> dict:
    """CLI/UI 文字列（locales/{lang}.json）を返す。"""
    return _load("locales", lang)


def load_prompts(lang: str | None = None) -> dict:
    """LLM プロンプト（prompts/{lang}.json）を返す。"""
    return _load("prompts", lang)


def clear_cache() -> None:
    """キャッシュを破棄する（テストの言語差リーク防止用）。"""
    _cache["locales"].clear()
    _cache["prompts"].clear()


def _t(loc: dict, section: str, name: str, default: str, **fmt) -> str:
    """ロケール文字列を取得する。引数名は `name`（`key` にすると `{key}` プレースホルダと
    衝突して TypeError になる）。`default` は日本語の安全弁（ストアにキーが無い場合のみ使用）。"""
    tmpl = loc.get(section, {}).get(name, default)
    return tmpl.format(**fmt) if fmt else tmpl


def peek_lang(argv: list[str]) -> str | None:
    """argv から `--lang X` / `--lang=X` を先読みする（argparse 構築前に help を現地化するため）。"""
    for i, a in enumerate(argv):
        if a == "--lang" and i + 1 < len(argv):
            return argv[i + 1]
        if a.startswith("--lang="):
            return a.split("=", 1)[1]
    return None


def add_lang_argument(parser: argparse.ArgumentParser) -> None:
    """全 CLI 共通の `--lang` を追加する。help は自己言及（--lang 自身は現地化できない）ため
    言語中立の英語で固定。"""
    parser.add_argument(
        "--lang",
        choices=list(_SUPPORTED),
        default=None,
        help=f"UI language (en/ja/zh; default: ${_ENV_VAR} or {_DEFAULT_LANG})",
    )


def translator(argv: list[str] | None = None):
    """argv から --lang を先読みして (lang, loc, t) を返す。argparse 構築前に使い、
    help 文字列を現地化する（構築前に --lang を解決するため）。t はその lang の
    ロケールにバインドされた翻訳関数。"""
    lang = resolve_lang(peek_lang(list(argv) if argv is not None else sys.argv[1:]))
    loc = load_locale(lang)

    def t(section: str, name: str, default: str, **fmt) -> str:
        return _t(loc, section, name, default, **fmt)

    return lang, loc, t
