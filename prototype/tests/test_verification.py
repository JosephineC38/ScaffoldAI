import json
import pytest

import architecture.verification as verification
from architecture.verification import (
  contains_stated_answer, _check_arithmetic, verify_answer, VALID_VERDICTS,
)


# --- contains_stated_answer -------------------------------------------------

@pytest.mark.parametrize("text,expected", [
  ("So delta U = 300 J, is that right?", True),
  ("I got 450 kJ, final answer?", True),
  ("Am I correct that W = 100 J?", True),
  ("Q = -50 kJ, right or wrong?", True),
  ("I got 450 kJ.", False),                      # digit, no confirmation phrase
  ("Is that correct in general?", False),        # confirmation phrase, no digit
  ("Can you explain the first law to me?", False),  # neither
])
def test_contains_stated_answer(text, expected):
  assert contains_stated_answer(text) is expected


# --- _check_arithmetic (pure/deterministic, no LLM) -------------------------

def test_check_arithmetic_correct_equation():
  result = _check_arithmetic("200 + 100 = 300")
  assert result["tier_result"] == "ARITHMETIC_OK"


def test_check_arithmetic_error_beyond_tolerance():
  result = _check_arithmetic("200 + 100 = 400")
  assert result["tier_result"] == "ARITHMETIC_ERROR"
  assert result["failing"]
  assert result["failing"][0]["computed"] == 300


def test_check_arithmetic_no_equation_found():
  result = _check_arithmetic("I think it's about 300 kJ but I'm not sure.")
  assert result["tier_result"] == "NO_EQUATION_FOUND"


def test_check_arithmetic_ignores_non_arithmetic_lhs_with_units():
  # "Q = -50 kJ" -- LHS "Q" fails _PURE_ARITHMETIC, so it's skipped, not misparsed.
  result = _check_arithmetic("Q = -50 kJ")
  assert result["tier_result"] == "NO_EQUATION_FOUND"


def test_check_arithmetic_within_tolerance_boundary_passes():
  # tolerance = max(abs(rhs)*0.01, 0.5); rhs=300 -> tolerance=3.0
  result = _check_arithmetic("200 + 102 = 300")
  assert result["tier_result"] == "ARITHMETIC_OK"


def test_check_arithmetic_just_outside_tolerance_boundary_fails():
  result = _check_arithmetic("200 + 104 = 300")
  assert result["tier_result"] == "ARITHMETIC_ERROR"


# --- verify_answer tier logic, _semantic_check mocked -----------------------

def _mock_semantic(monkeypatch, verdict, correct_value="300", called_tracker=None):
  def fake(problem_statement, student_answer, topic):
    if called_tracker is not None:
      called_tracker.append(True)
    return {
      "correct_value": correct_value,
      "verdict": verdict,
      "step_by_step_reasoning": "mocked reasoning",
    }
  monkeypatch.setattr(verification, "_semantic_check", fake)


def test_verify_answer_arithmetic_error_and_semantic_correct_is_disagreement(monkeypatch):
  _mock_semantic(monkeypatch, verdict="CORRECT")
  result = verify_answer("A student computes W.", "200 + 100 = 400", "Laws of Thermodynamics")
  assert result["tier"] == "disagreement"
  assert result["verdict"] == "UNCERTAIN"


def test_verify_answer_arithmetic_error_and_semantic_incorrect_is_deterministic(monkeypatch):
  _mock_semantic(monkeypatch, verdict="INCORRECT")
  result = verify_answer("A student computes W.", "200 + 100 = 400", "Laws of Thermodynamics")
  assert result["tier"] == "deterministic"
  assert result["verdict"] == "INCORRECT"  # forced, regardless of semantic's own verdict


def test_verify_answer_no_arithmetic_error_defers_to_semantic(monkeypatch):
  for verdict in VALID_VERDICTS:
    _mock_semantic(monkeypatch, verdict=verdict)
    result = verify_answer("A student computes W.", "200 + 100 = 300", "Laws of Thermodynamics")
    assert result["tier"] == "semantic"
    assert result["verdict"] == verdict


def test_verify_answer_calls_semantic_check_even_when_arithmetic_is_clean(monkeypatch):
  called = []
  _mock_semantic(monkeypatch, verdict="CORRECT", called_tracker=called)
  verify_answer("A student computes W.", "200 + 100 = 300", "Laws of Thermodynamics")
  assert called == [True]  # cost implication: every verify_answer() call is a live gpt-4o call


def test_verify_answer_calls_semantic_check_even_with_no_equation(monkeypatch):
  called = []
  _mock_semantic(monkeypatch, verdict="UNCERTAIN", called_tracker=called)
  verify_answer("A student computes W.", "I think it's about 300 kJ", "Laws of Thermodynamics")
  assert called == [True]


# --- _semantic_check robustness gap: no error handling around the API call -

def test_semantic_check_propagates_api_exception_uncaught(monkeypatch):
  def raising_create(**kwargs):
    raise RuntimeError("simulated API failure")

  monkeypatch.setattr(verification.client.chat.completions, "create", raising_create)

  with pytest.raises(RuntimeError, match="simulated API failure"):
    verification._semantic_check("problem", "answer", "Laws of Thermodynamics")


def test_semantic_check_propagates_malformed_json_uncaught(monkeypatch, make_openai_response):
  def bad_json_create(**kwargs):
    return make_openai_response("not valid json{{{")

  monkeypatch.setattr(verification.client.chat.completions, "create", bad_json_create)

  with pytest.raises(json.JSONDecodeError):
    verification._semantic_check("problem", "answer", "Laws of Thermodynamics")


def test_verify_answer_propagates_semantic_check_failure_uncaught(monkeypatch):
  def raising_semantic(*args, **kwargs):
    raise RuntimeError("simulated API failure")

  monkeypatch.setattr(verification, "_semantic_check", raising_semantic)

  with pytest.raises(RuntimeError, match="simulated API failure"):
    verify_answer("problem", "200 + 100 = 300", "Laws of Thermodynamics")
