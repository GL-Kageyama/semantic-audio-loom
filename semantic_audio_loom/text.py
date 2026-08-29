"""台詞テキストの前処理（ふりがな＝読みの指定）。

Tsukasa の phonemize（cutlet / UniDic）が一部の漢字を誤読する（例：「既読」→ kijomi）。
正しい読みは、かなを直接渡せば再現できるため、台詞に `漢字《かな》` のルビを振って
読みを指定できるようにする。

`parse_ruby` は台詞を
- `dialogue` … `《》` を除去した綺麗な文（表示・sha1 の対象）
- `reading`  … ルビをかなへ置換した本文（phonemize の入力。ルビが無ければ空文字）
に分解する。未アノテーションの漢字は従来どおり cutlet が読む（`reading` はかなと
漢字が混在したまま phonemize に渡る）。
"""
from __future__ import annotations

import re

# ルビ記法: 直前の「単語」（かな・漢字・英数字・長音）を「漢字」、`《》` 内を「かな」とする。
# 句読点（、。等）は基底に含めない＝複数ルビが隣接しても区切りを跨いで食わない。
# 例: 既読《きどく》 → 漢字=既読 / かな=きどく
_RUBY_BASE = r"[ぁ-んァ-ンー一-龠々0-9A-Za-z]+?"
_RUBY = re.compile(rf"({_RUBY_BASE})《([^》]+)》")


def annotate_reading(text: str, word: str, reading: str) -> str:
    """text 中の word（ルビ未指定のもの）に `word《reading》` を付ける。

    既に `word《…》` と振られている箇所には二重に付けない（negative lookahead）。
    word が text に含まれない場合は無変更。固有名詞（キャラ名など）の読み指定に使う。
    """
    if not word or not reading or word not in text:
        return text
    return re.sub(re.escape(word) + r"(?!《)", f"{word}《{reading}》", text)


def parse_ruby(text: str) -> tuple[str, str]:
    """ふりがな《》記法を解釈し、(表示用台詞, 読み) を返す。

    ルビが無い（`《`/`》` が揃っていない）場合は `(text, "")`。
    """
    if not text or "《" not in text or "》" not in text:
        return text, ""
    dialogue = _RUBY.sub(r"\1", text)  # 《...》を除去 → 綺麗な台詞
    reading = _RUBY.sub(r"\2", text)   # 漢字《かな》→ かな（本文）
    return dialogue, reading
