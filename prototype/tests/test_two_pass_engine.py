import json
import pytest

import architecture.two_pass_engine as tpe
from architecture.two_pass_engine import (
  has_problem_context, generate_response, _extract_verification_inputs,
)


# --- has_problem_context -----------------------------------------------------

@pytest.mark.parametrize("message,expected", [
  ("I got a delta U of 12.5 in this step", True),      # decimal number
  ("So Q equals 300 in this case", True),               # multi-digit number
  ("The process happens at 300 kPa", True),              # unit near number
  ("It cools down to 20K over the run", True),           # short unit near number
  ("I'm stuck on a Carnot efficiency problem", True),    # problem-reference phrase
  ("This problem gives me the following values", True),  # "this problem" phrase
  ("Q11 asks about the rankine cycle", False),           # multi-digit inside a token, word-boundary excluded
  ("Why does the second law hold?", False),              # bare factual, no evidence
  ("What is the Rankine cycle used for?", False),        # bare factual, no evidence
  ("What is the Carnot efficiency formula used for in practice?", False),
])
def test_has_problem_context(message, expected):
  assert has_problem_context([], message) is expected


def test_has_problem_context_scans_recent_conversation_history_too():
  history = [{"role": "user", "content": "Earlier I calculated 300 kJ for this system."}]
  assert has_problem_context(history, "Is that the right approach?") is True


def test_has_problem_context_short_unit_letter_alone_is_not_evidence():
  assert has_problem_context([], "Kelvin is a temperature scale, what is K used for?") is False


# --- _extract_verification_inputs --------------------------------------------

def test_extract_verification_inputs_only_pulls_from_user_turns():
  history = [
    {"role": "user", "content": "I calculated Q = 300 kJ for this system."},
    {"role": "assistant", "content": "Are you sure about 999 kJ there?"},
  ]
  problem_statement, student_answer = _extract_verification_inputs("Is that right?", history)
  assert "999" not in problem_statement
  assert "300" in problem_statement
  assert student_answer == "Is that right?"


def test_extract_verification_inputs_falls_back_to_user_input_with_no_numeric_history():
  problem_statement, student_answer = _extract_verification_inputs("Is 300 kJ right?", [])
  assert problem_statement == "Is 300 kJ right?"
  assert student_answer == "Is 300 kJ right?"


# --- generate_response: IRL -> CONCEPTUAL override wiring --------------------

def _mock_pass_one(monkeypatch, make_openai_response, classification, topic="Laws of Thermodynamics"):
  content = json.dumps({
    "topic": topic,
    "classification": classification,
    "reasoning_gap": "mocked reasoning gap",
    "misconception": None,
  })

  def fake_create(**kwargs):
    return make_openai_response(content, prompt_tokens=50, completion_tokens=20)

  monkeypatch.setattr(tpe.client.chat.completions, "create", fake_create)


def test_generate_response_applies_irl_to_conceptual_override(monkeypatch, make_openai_response):
  _mock_pass_one(monkeypatch, make_openai_response, classification="IRL")

  captured = {}

  def stub_handler(user_input, diagnosis, topic, conversation_history, verification, system_prompt):
    captured["diagnosis"] = json.loads(diagnosis)
    return "stub response", True

  monkeypatch.setattr(tpe, "MODE_HANDLERS", {**tpe.MODE_HANDLERS, "Hint-only": stub_handler})

  _, _, diagnostics = generate_response("Why does the second law hold?", [], "Hint-only")

  assert diagnostics["classification"] == "CONCEPTUAL"
  assert captured["diagnosis"]["classification"] == "CONCEPTUAL"


def test_generate_response_leaves_irl_alone_when_problem_context_exists(monkeypatch, make_openai_response):
  _mock_pass_one(monkeypatch, make_openai_response, classification="IRL")

  def stub_handler(user_input, diagnosis, topic, conversation_history, verification, system_prompt):
    return "stub response", False

  monkeypatch.setattr(tpe, "MODE_HANDLERS", {**tpe.MODE_HANDLERS, "Hint-only": stub_handler})

  _, _, diagnostics = generate_response("I'm stuck on a Carnot efficiency problem with 300 K", [], "Hint-only")

  assert diagnostics["classification"] == "IRL"


# --- generate_response: sanitization dispatch wiring -------------------------

def test_generate_response_skips_sanitization_when_gave_direct_answer_true(monkeypatch, make_openai_response):
  _mock_pass_one(monkeypatch, make_openai_response, classification="CONCEPTUAL")

  def stub_handler(user_input, diagnosis, topic, conversation_history, verification, system_prompt):
    return "The answer is 42 kJ, therefore we obtain the result.", True

  monkeypatch.setattr(tpe, "MODE_HANDLERS", {**tpe.MODE_HANDLERS, "Hint-only": stub_handler})

  pass_three_called = []
  monkeypatch.setattr(tpe, "pass_three", lambda *a, **k: pass_three_called.append(True))

  response_text, _, _ = generate_response("What is entropy?", [], "Hint-only")

  assert pass_three_called == []
  assert response_text == "The answer is 42 kJ, therefore we obtain the result."


def test_generate_response_sanitizes_when_gave_direct_answer_false_and_phrase_detected(monkeypatch, make_openai_response):
  _mock_pass_one(monkeypatch, make_openai_response, classification="IPS")

  def stub_handler(user_input, diagnosis, topic, conversation_history, verification, system_prompt):
    return "Therefore the value is revealed here.", False

  monkeypatch.setattr(tpe, "MODE_HANDLERS", {**tpe.MODE_HANDLERS, "Hint-only": stub_handler})

  pass_three_calls = []

  def stub_pass_three(leaked_response, topic):
    pass_three_calls.append(leaked_response)
    return "Sanitized response."

  monkeypatch.setattr(tpe, "pass_three", stub_pass_three)

  response_text, _, _ = generate_response("I tried this and got stuck.", [], "Hint-only")

  assert pass_three_calls == ["Therefore the value is revealed here."]
  assert response_text == "Sanitized response."


def test_generate_response_leaves_response_alone_when_no_phrase_detected(monkeypatch, make_openai_response):
  _mock_pass_one(monkeypatch, make_openai_response, classification="IPS")

  def stub_handler(user_input, diagnosis, topic, conversation_history, verification, system_prompt):
    return "Can you tell me which direction heat is flowing here?", False

  monkeypatch.setattr(tpe, "MODE_HANDLERS", {**tpe.MODE_HANDLERS, "Hint-only": stub_handler})

  pass_three_called = []
  monkeypatch.setattr(tpe, "pass_three", lambda *a, **k: pass_three_called.append(True))

  response_text, _, _ = generate_response("I tried this and got stuck.", [], "Hint-only")

  assert pass_three_called == []
  assert response_text == "Can you tell me which direction heat is flowing here?"
