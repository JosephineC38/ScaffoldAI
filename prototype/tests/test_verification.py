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
  def fake(problem_statement, student_answer, topic, proposed_value):
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
  result = verify_answer("A student computes W.", "200 + 100 = 400", "Laws of Thermodynamics", "400")
  assert result["tier"] == "disagreement"
  assert result["verdict"] == "UNCERTAIN"


def test_verify_answer_arithmetic_error_and_semantic_incorrect_is_deterministic(monkeypatch):
  _mock_semantic(monkeypatch, verdict="INCORRECT")
  result = verify_answer("A student computes W.", "200 + 100 = 400", "Laws of Thermodynamics", "400")
  assert result["tier"] == "deterministic"
  assert result["verdict"] == "INCORRECT"  # forced, regardless of semantic's own verdict


def test_verify_answer_no_arithmetic_error_defers_to_semantic(monkeypatch):
  for verdict in VALID_VERDICTS:
    _mock_semantic(monkeypatch, verdict=verdict)
    result = verify_answer("A student computes W.", "200 + 100 = 300", "Laws of Thermodynamics", "300")
    assert result["tier"] == "semantic"
    assert result["verdict"] == verdict


def test_verify_answer_calls_semantic_check_even_when_arithmetic_is_clean(monkeypatch):
  called = []
  _mock_semantic(monkeypatch, verdict="CORRECT", called_tracker=called)
  verify_answer("A student computes W.", "200 + 100 = 300", "Laws of Thermodynamics", "300")
  assert called == [True]  # cost implication: every verify_answer() call is a live gpt-4o call


def test_verify_answer_calls_semantic_check_even_with_no_equation(monkeypatch):
  called = []
  _mock_semantic(monkeypatch, verdict="UNCERTAIN", called_tracker=called)
  verify_answer("A student computes W.", "I think it's about 300 kJ", "Laws of Thermodynamics", "300 kJ")
  assert called == [True]


# --- _semantic_check robustness gap: no error handling around the API call -

def test_semantic_check_propagates_api_exception_uncaught(monkeypatch):
  def raising_create(**kwargs):
    raise RuntimeError("simulated API failure")

  monkeypatch.setattr(verification.client.chat.completions, "create", raising_create)

  with pytest.raises(RuntimeError, match="simulated API failure"):
    verification._semantic_check("problem", "answer", "Laws of Thermodynamics", "300 kJ")


def test_semantic_check_propagates_malformed_json_uncaught(monkeypatch, make_openai_response):
  def bad_json_create(**kwargs):
    return make_openai_response("not valid json{{{")

  monkeypatch.setattr(verification.client.chat.completions, "create", bad_json_create)

  with pytest.raises(json.JSONDecodeError):
    verification._semantic_check("problem", "answer", "Laws of Thermodynamics", "300 kJ")


def test_verify_answer_propagates_semantic_check_failure_uncaught(monkeypatch):
  def raising_semantic(*args, **kwargs):
    raise RuntimeError("simulated API failure")

  monkeypatch.setattr(verification, "_semantic_check", raising_semantic)

  with pytest.raises(RuntimeError, match="simulated API failure"):
    verify_answer("problem", "200 + 100 = 300", "Laws of Thermodynamics", "300")


# --- proposed_value replaces regex extraction as the source of truth ---------

def test_semantic_check_compares_against_proposed_value_not_last_equals(monkeypatch):
  """The TC01 regression: the student states their answer FIRST and their
  formula/constants after it. _last_stated_number() picked up the trailing
  constant (0.718) and the deterministic override then manufactured INCORRECT
  against a model derivation that agreed with the student. The comparison must
  now use the passed-in proposed_value instead."""
  monkeypatch.setattr(verification, "get_reference", lambda topic: "ref")

  class _Msg:
    content = json.dumps({"correct_value": "215.4 kJ", "verdict": "CORRECT",
                          "step_by_step_reasoning": "m*cv*dT"})

  class _Choice:
    message = _Msg()

  class _Usage:
    prompt_tokens = 1
    completion_tokens = 1

  class _Resp:
    choices = [_Choice()]
    usage = _Usage()

  monkeypatch.setattr(verification.client.chat.completions, "create", lambda **k: _Resp())

  student_text = ("I calculated Q = 215.4 kJ using Q = m·cv·ΔT with "
                  "cv = 0.718 kJ/kg·K. Is that right?")
  # The old path would have extracted this, and been wrong:
  assert verification._extract_number(verification._last_stated_number(student_text)) == 0.718

  result = verification._semantic_check("problem", student_text,
                                        "Heat, Work, and Energy Transfer", "215.4 kJ")
  assert result["verdict"] == "CORRECT"


def test_semantic_check_qualitative_claim_defers_to_model_verdict(monkeypatch):
  """A directional claim has no number, so the deterministic override cannot
  apply and must leave the semantic verdict untouched rather than failing."""
  monkeypatch.setattr(verification, "get_reference", lambda topic: "ref")

  class _Msg:
    content = json.dumps({"correct_value": "positive", "verdict": "CORRECT",
                          "step_by_step_reasoning": "work in, Q=0"})

  class _Choice:
    message = _Msg()

  class _Usage:
    prompt_tokens = 1
    completion_tokens = 1

  class _Resp:
    choices = [_Choice()]
    usage = _Usage()

  monkeypatch.setattr(verification.client.chat.completions, "create", lambda **k: _Resp())

  result = verification._semantic_check("problem", "I think it should be positive",
                                        "Heat, Work, and Energy Transfer", "positive")
  assert result["verdict"] == "CORRECT"
