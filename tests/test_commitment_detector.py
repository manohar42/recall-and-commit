from datetime import datetime, timezone

from app.services.commitment_detector import detect_commitment, parse_due


def test_detects_proposal_promise():
    r = detect_commitment("I will send you the revised proposal by Friday afternoon.", ("Maya",))
    assert r is not None
    assert r.action_text == "send you the revised proposal"
    assert r.due_text.lower() == "by friday afternoon"
    assert r.counterparty == "Maya"


def test_ignores_questions_negations_and_hedges():
    assert detect_commitment("Will you send me the file?") is None
    assert detect_commitment("I won't be able to send the report.") is None
    assert detect_commitment("Maybe I'll send the report tomorrow.") is None
    assert detect_commitment("The gray model has better battery life.") is None


def test_parse_due_resolves_relative_to_reference():
    ref = datetime(2026, 9, 28, 10, 0, tzinfo=timezone.utc)  # Monday
    assert parse_due("by Friday afternoon", ref).day == 2  # Oct 2
    assert parse_due("next week", ref) is None
    assert parse_due("by Friday", None) is None