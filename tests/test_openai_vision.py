from app.services.openai_vision import _signal_from_score


def test_signal_thresholds_are_more_permissive() -> None:
    assert _signal_from_score(24) == "red"
    assert _signal_from_score(25) == "yellow"
    assert _signal_from_score(59) == "yellow"
    assert _signal_from_score(60) == "blue"
