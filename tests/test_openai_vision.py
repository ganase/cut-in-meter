from app.services.openai_vision import SYSTEM_PROMPT, _apply_visibility_rules, _signal_from_score


def test_signal_thresholds_are_more_permissive() -> None:
    assert _signal_from_score(24) == "red"
    assert _signal_from_score(25) == "yellow"
    assert _signal_from_score(59) == "yellow"
    assert _signal_from_score(60) == "blue"


def test_prompt_requires_smiles_blue_and_no_face_red() -> None:
    assert "smiling or softly smiling, return blue" in SYSTEM_PROMPT
    assert "If no face is visible" in SYSTEM_PROMPT


def test_no_face_is_forced_to_red() -> None:
    parsed = _apply_visibility_rules(
        {
            "score": 88,
            "signal": "blue",
            "confidence": 90,
            "faceVisible": False,
            "smiling": True,
            "headline": "ignored",
            "reasons": ["a", "b"],
            "playfulSuggestion": "ignored",
            "caution": "note",
        }
    )
    assert parsed["signal"] == "red"
    assert parsed["score"] == 15


def test_smile_is_forced_to_blue() -> None:
    parsed = _apply_visibility_rules(
        {
            "score": 40,
            "signal": "yellow",
            "confidence": 90,
            "faceVisible": True,
            "smiling": True,
            "headline": "ignored",
            "reasons": ["a", "b"],
            "playfulSuggestion": "ignored",
            "caution": "note",
        }
    )
    assert parsed["signal"] == "blue"
    assert parsed["score"] == 75
