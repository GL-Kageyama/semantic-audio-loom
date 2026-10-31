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


def test_moderate_intensity_adds_no_phrase():
    """中庸（0.35〜0.65）は余計な一言を足さない。感情の文言だけで足りる。"""
    moderate = tsukasa._spec_prompt("A voice.", _spec(0.55))
    assert "faint" not in moderate
    assert "strong" not in moderate
    assert "overwhelming" not in moderate


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
