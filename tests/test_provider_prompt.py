"""Provider の散文（Spec → 生成モデルへの演技指示）の検査。

散文は音そのものではないが、散文に載らない指示は音にも載らない。
「強度を振ったのに音がバイト一致した」のは、強度が散文へ渡っていなかったため。
"""
from semantic_audio_loom.providers import tsukasa


def _spec(intensity, primary="anger"):
    return {
        "emotion": {"primary": primary, "intensity": intensity},
        "delivery": "suppressed",
        "loudness": {"effort": "normal"},
        "prosody": {"pace": "natural", "intonation": "flat"},
    }


def test_intensity_reaches_the_prompt():
    """同じ感情でも、強度が違えば散文が違い、同じ強度なら同じになる。"""
    weak = tsukasa._spec_prompt("A voice.", _spec(0.35))
    strong = tsukasa._spec_prompt("A voice.", _spec(0.95))
    assert weak != strong
    assert tsukasa._spec_prompt("A voice.", _spec(0.95)) == strong
    assert "faint" in weak and "overwhelming" in strong


def test_intensity_none_adds_no_phrase():
    """Direction の intensity=none（0.0）に「かすかに」を足さない。

    抽象の語と散文が逆向きになる（none が faint になる）と、Direction の
    一番弱い指示が一番弱い演技ではなく「かすかな演技」になる。
    """
    prompt = tsukasa._spec_prompt("A voice.", _spec(0.0))
    assert "faint" not in prompt
    assert "faint" in tsukasa._spec_prompt("A voice.", _spec(0.25))


def test_moderate_intensity_has_its_own_phrase():
    """中庸（0.41〜0.70）にも強度の文言を 1 つ置く（4 段すべてが別の文になる）。

    空だと moderate は「強度に何も言わない」文になり、strong と同じになる。
    """
    moderate = tsukasa._spec_prompt("A voice.", _spec(0.55))
    assert "moderately strong" in moderate
    assert "faint" not in moderate
    assert "overwhelming" not in moderate
    phrases = {tsukasa._intensity_phrase(v) for v in (0.3, 0.5, 0.8, 1.0)}
    assert len(phrases) == 4


def test_intensity_bands_are_ordered_and_disjoint():
    """帯の上端の境目で、文言が 1 つずつ進む（0.40 faint / 0.41 中庸 / 0.70 中庸 / 0.71 strong）。"""
    assert "faint" in tsukasa._intensity_phrase(0.40)
    assert "moderately" in tsukasa._intensity_phrase(0.41)
    assert "moderately" in tsukasa._intensity_phrase(0.70)
    assert "close to the surface" in tsukasa._intensity_phrase(0.71)
    assert "at its limit" in tsukasa._intensity_phrase(1.0)


def test_whisper_reaches_the_prompt():
    """声量は direction の値（whisper）を優先する。effort の "quietly" に潰さない。"""
    spec = _spec(0.55)
    spec["loudness"] = {"effort": "relaxed", "volume": "whisper"}
    prompt = tsukasa._spec_prompt("A voice.", spec)
    assert "barely above a whisper" in prompt
    assert "quietly" not in prompt


def test_rule_resolve_keeps_the_volume():
    """rule の写像で volume が Spec に残る（effort だけだと囁きが消える）。"""
    from semantic_audio_loom.engine import resolve
    from semantic_audio_loom.types import GenerationIntent

    intent = GenerationIntent(
        asset_type="voice",
        voice_profile={},
        emotion={"primary": "calm", "intensity": "subtle"},
        performance={"volume": "whisper"},
    )
    spec = resolve.resolve_rule(intent)
    assert spec["loudness"]["volume"] == "whisper"
    assert spec["loudness"]["effort"] == "relaxed"


def test_pitch_reaches_the_prompt():
    """語尾の上げ下げだけでは「同じ台詞の三通り」が二通りに潰れる。高さも散文に載せる。"""
    low = _spec(0.55)
    low["prosody"] = {"pace": "natural", "pitch": "low"}
    high = _spec(0.55)
    high["prosody"] = {"pace": "natural", "pitch": "slightly_high"}
    assert "with a low pitch" in tsukasa._spec_prompt("A voice.", low)
    assert "with a slightly higher pitch" in tsukasa._spec_prompt("A voice.", high)
    natural = _spec(0.55)
    natural["prosody"] = {"pace": "natural", "pitch": "natural"}
    assert "pitch" not in tsukasa._spec_prompt("A voice.", natural).replace("pitch falling", "")


def test_intensity_missing_does_not_break_the_prompt():
    """intensity が無い（0 や None）Spec でも散文は作れる。"""
    for value in (None, 0, "0.0"):
        prompt = tsukasa._spec_prompt("A voice.", _spec(value))
        assert "A voice." in prompt and prompt.endswith(". ")


def test_rule_resolve_carries_the_intonation():
    """語尾の抑揚は Direction から Spec へ通す（rule でも指定できる）。"""
    from semantic_audio_loom.engine import resolve
    from semantic_audio_loom.types import GenerationIntent

    intent = GenerationIntent(
        asset_type="voice",
        voice_profile={},
        emotion={"primary": "sadness", "intensity": "moderate"},
        performance={"intonation": "falling"},
    )
    spec = resolve.resolve_rule(intent)
    assert spec["prosody"]["intonation"] == "falling"
    assert "pitch falling at the end" in tsukasa._spec_prompt("A voice.", spec)
    # 指定が無ければ neutral（従来どおり）。
    none = GenerationIntent(asset_type="voice", voice_profile={},
                            emotion={"primary": "neutral"}, performance={})
    assert resolve.resolve_rule(none)["prosody"]["intonation"] == "neutral"


def test_rule_resolve_carries_the_breathiness():
    """息の混じり方も Direction から Spec へ通す（散文に載らなければ音にも載らない）。"""
    from semantic_audio_loom.engine import resolve
    from semantic_audio_loom.types import GenerationIntent

    intent = GenerationIntent(
        asset_type="voice",
        voice_profile={},
        emotion={"primary": "neutral", "intensity": "moderate"},
        performance={"breathiness": "heavy"},
    )
    spec = resolve.resolve_rule(intent)
    assert spec["prosody"]["breathiness"] == "heavy"
    assert "breathy" in tsukasa._spec_prompt("A voice.", spec)
    # none は一言も足さない（既定を汚さない）。
    plain = GenerationIntent(asset_type="voice", voice_profile={},
                             emotion={"primary": "neutral"}, performance={})
    assert resolve.resolve_rule(plain)["prosody"]["breathiness"] == "none"
    assert "breathy" not in tsukasa._spec_prompt("A voice.", resolve.resolve_rule(plain))


SCHEMA = "schemas/performance_spec.schema.json"


def _enum(path):
    import json
    from pathlib import Path

    spec = json.loads(Path(SCHEMA).read_text())
    for key in path:
        spec = spec["properties"][key]
    return spec["enum"]


def _with(path, value):
    """既定の Spec に 1 欄だけ値を入れた散文を作る。"""
    spec = _spec(0.5, primary="neutral")
    spec.pop("delivery", None)
    cur = spec
    for key in path[:-1]:
        cur = cur.setdefault(key, {})
    cur[path[-1]] = value
    return tsukasa._spec_prompt("A voice.", spec)


def test_every_enum_value_reaches_the_prompt():
    """Schema の列挙値をすべて散文に載せる（欄の脱落を列挙で捕まえる）。

    息（breathiness）は Schema・CLI・Direction が受けるのに、散文に載らず
    heavy と none がバイト一致していた。列挙値ごとに散文を比べれば、
    二つの値が同じ文になる（＝どちらかが捨てられている）ことを検出できる。
    """
    fields = [
        (["emotion"], "primary"),
        (["prosody"], "pace"),
        (["prosody"], "pitch"),
        (["prosody"], "intonation"),
        (["prosody"], "breathiness"),
        ([], "delivery"),
        (["loudness"], "volume"),
    ]
    for keys, field in fields:
        path = keys + [field]
        values = _enum(path)
        prompts = {v: _with(path, v) for v in values}
        unique = {p for p in prompts.values()}
        assert len(unique) == len(values), (
            f"{'.'.join(path)}: 列挙 {len(values)} のうち散文が {len(unique)} 通り"
            f"（潰れた値: {[v for v in values if list(prompts.values()).count(prompts[v]) > 1]}）"
        )


def test_effort_alone_reaches_the_prompt_but_volume_wins():
    """張り（effort）は volume が無いときだけ散文に出る（三層分業の実装）。"""
    spec = _spec(0.5)
    spec["loudness"] = {"effort": "strained"}
    assert "shouting" in tsukasa._spec_prompt("A voice.", spec)
    spec["loudness"] = {"effort": "strained", "volume": "whisper"}
    prompt = tsukasa._spec_prompt("A voice.", spec)
    assert "barely above a whisper" in prompt and "shouting" not in prompt


def test_subtext_is_carried_but_never_reaches_the_prompt():
    """subtext は Spec まで来るが、散文にはならない（`--resolve rule` の実測）。

    台詞の裏の意味を 5 通りに振って 25 本焼いても、seed 4 通りは md5 が一致した
    （`projects/longform/experiments/subtext/acting-subtext/`）。載っていないのを検査で固定する。
    """
    from semantic_audio_loom.engine.resolve import resolve_rule
    from semantic_audio_loom.types import GenerationIntent

    prompts = set()
    for subtext in ("", "本当は帰りたい", "もう来ないつもりだ", "怒っている"):
        intent = GenerationIntent(
            dialogue="明日、また来るね。", subtext=subtext,
            emotion={"primary": "neutral", "intensity": "moderate"},
        )
        spec = resolve_rule(intent)
        assert spec["subtext"] == subtext          # Spec には載る
        prompts.add(tsukasa._spec_prompt("A voice.", spec))
    assert len(prompts) == 1                        # 散文は 1 通り


def test_intensity_band_below_and_at_040():
    """「the feeling is faint」は 0.40 まで（0.41 では付かない）。実測の境目を固定。"""
    assert "faint" in tsukasa._spec_prompt("A voice.", _spec(0.40))
    assert "faint" not in tsukasa._spec_prompt("A voice.", _spec(0.41))
