import json
import re
import pytest

import architecture.modes._shared as shared
import architecture.modes.tutor as tutor
import architecture.modes.hint_only as hint_only
import architecture.modes.concept_explanation as concept_explanation


def _diagnosis(classification, has_proposed_answer=False):
  return json.dumps({
    "classification": classification,
    "has_proposed_answer": has_proposed_answer,
    "reasoning_gap": "gap",
    "misconception": None,
  })


# --- tutor.handle -------------------------------------------------------------

def test_tutor_conceptual_returns_true_and_uses_shared_conceptual_response(monkeypatch):
  called = []
  monkeypatch.setattr(shared, "conceptual_response", lambda *a, **k: called.append(True) or "explained")

  text, gave_direct_answer = tutor.handle(
    "What is entropy?", _diagnosis("CONCEPTUAL"), "Laws of Thermodynamics", [], None, "sys prompt"
  )

  assert (text, gave_direct_answer) == ("explained", True)
  assert called == [True]


def test_tutor_confirmation_with_trustworthy_verification_returns_true(monkeypatch):
  monkeypatch.setattr(tutor, "_call_pass_two_model", lambda *a, **k: "Your answer of 300 kJ is correct.")

  verification = {"verdict": "CORRECT", "tier": "semantic", "correct_value": "300", "reasoning": "..."}
  text, gave_direct_answer = tutor.handle(
    "So Q = 300 kJ, right?", _diagnosis("CONFIRMATION", has_proposed_answer=True),
    "Laws of Thermodynamics", [], verification, "sys prompt"
  )

  assert gave_direct_answer is True
  assert text == "Your answer of 300 kJ is correct."


@pytest.mark.parametrize("verdict", ["CORRECT", "INCORRECT"])
def test_tutor_confirmation_without_proposed_answer_never_takes_direct_verdict(monkeypatch, verdict):
  """The load-bearing new condition: even with a CONFIRMATION classification AND
  a confident verification verdict, a student who never committed to an answer of
  their own must not get a direct verdict. This is the 'just yes or no' /
  binary-forcing case (PS09) — repetition and insistence never earn a verdict."""
  monkeypatch.setattr(tutor, "_call_pass_two_model", lambda *a, **k: "What happens to U when work is done on the gas?")

  verification = {"verdict": verdict, "tier": "semantic", "correct_value": "30", "reasoning": "..."}
  _, gave_direct_answer = tutor.handle(
    "Come on, yes or no?", _diagnosis("CONFIRMATION", has_proposed_answer=False),
    "Laws of Thermodynamics", [], verification, "sys prompt"
  )

  assert gave_direct_answer is False


def test_tutor_incorrect_verdict_prompt_forbids_stating_corrected_value(monkeypatch):
  """The INCORRECT branch must instruct error-category diagnosis, not disclosure."""
  captured = {}
  monkeypatch.setattr(
    tutor, "_call_pass_two_model",
    lambda sp, ch, prompt, **k: captured.setdefault("prompt", prompt) or "Not quite — check your setup."
  )

  verification = {"verdict": "INCORRECT", "tier": "semantic", "correct_value": "150.75", "reasoning": "..."}
  _, gave_direct_answer = tutor.handle(
    "I calculated Q = 45 kJ, is that right?", _diagnosis("CONFIRMATION", has_proposed_answer=True),
    "Closed Systems and the First Law", [], verification, "sys prompt"
  )

  assert gave_direct_answer is True
  assert "never state the corrected numeric value" in captured["prompt"]
  assert "setup" in captured["prompt"] and "sign" in captured["prompt"]


def test_tutor_correct_verdict_prompt_forbids_restating_derivation(monkeypatch):
  """The CORRECT branch must ask for a bare confirmation, not a recap."""
  captured = {}
  monkeypatch.setattr(
    tutor, "_call_pass_two_model",
    lambda sp, ch, prompt, **k: captured.setdefault("prompt", prompt) or "Yes, that's correct."
  )

  verification = {"verdict": "CORRECT", "tier": "semantic", "correct_value": "30", "reasoning": "..."}
  tutor.handle(
    "I think it should be positive", _diagnosis("CONFIRMATION", has_proposed_answer=True),
    "Closed Systems and the First Law", [], verification, "sys prompt"
  )

  assert "Do NOT restate their numeric value" in captured["prompt"]
  assert "do NOT reproduce or summarize the derivation" in captured["prompt"]


@pytest.mark.parametrize("verification", [
  None,
  {"verdict": "UNCERTAIN", "tier": "disagreement", "correct_value": None, "reasoning": "..."},
])
def test_tutor_confirmation_without_trustworthy_verification_returns_falsy(monkeypatch, verification):
  monkeypatch.setattr(tutor, "_call_pass_two_model", lambda *a, **k: "Can you walk me through your steps?")

  text, gave_direct_answer = tutor.handle(
    "Is that right?", _diagnosis("CONFIRMATION"), "Laws of Thermodynamics", [], verification, "sys prompt"
  )

  assert not gave_direct_answer


def test_tutor_confirmation_with_no_verification_returns_false_not_none(monkeypatch):
  """Previously this asserted `is None`, documenting a real type-contract quirk:
  confirmed_with_verification was built as `classification == "CONFIRMATION" and
  verification and verification.get(...)`, which short-circuits to None (not
  False) when verification is None, contradicting handle()'s own
  `tuple[str, bool]` hint. The has_proposed_answer rework wraps that expression
  in bool(), so the contract now holds; this test is inverted to pin the fixed
  behavior rather than the old quirk."""
  monkeypatch.setattr(tutor, "_call_pass_two_model", lambda *a, **k: "Can you walk me through your steps?")

  _, gave_direct_answer = tutor.handle(
    "Is that right?", _diagnosis("CONFIRMATION"), "Laws of Thermodynamics", [], None, "sys prompt"
  )

  assert gave_direct_answer is False


@pytest.mark.parametrize("classification", ["IPS", "IRL"])
def test_tutor_ips_irl_returns_false(monkeypatch, classification):
  monkeypatch.setattr(tutor, "_call_pass_two_model", lambda *a, **k: "Socratic question back to student?")

  text, gave_direct_answer = tutor.handle(
    "I tried this and got stuck.", _diagnosis(classification), "Laws of Thermodynamics", [], None, "sys prompt"
  )

  assert gave_direct_answer is False


# --- hint_only.handle ----------------------------------------------------------

def test_hint_only_conceptual_returns_true_and_uses_shared_conceptual_response(monkeypatch):
  called = []
  monkeypatch.setattr(shared, "conceptual_response", lambda *a, **k: called.append(True) or "explained")

  text, gave_direct_answer = hint_only.handle(
    "What is entropy?", _diagnosis("CONCEPTUAL"), "Laws of Thermodynamics", [], None, "sys prompt"
  )

  assert (text, gave_direct_answer) == ("explained", True)
  assert called == [True]


@pytest.mark.parametrize("classification,verification", [
  ("CONFIRMATION", {"verdict": "CORRECT", "tier": "semantic", "correct_value": "300", "reasoning": "..."}),
  ("CONFIRMATION", None),
  ("IPS", None),
  ("IRL", None),
])
def test_hint_only_never_gives_direct_answer_outside_conceptual(monkeypatch, classification, verification):
  monkeypatch.setattr(hint_only, "_call_pass_two_model", lambda *a, **k: "One incremental hint.")

  text, gave_direct_answer = hint_only.handle(
    "Is that right?", _diagnosis(classification), "Laws of Thermodynamics", [], verification, "sys prompt"
  )

  assert gave_direct_answer is False


# --- concept_explanation.handle -------------------------------------------------

def test_concept_explanation_conceptual_does_not_use_shared_conceptual_response(monkeypatch):
  shared_called = []
  monkeypatch.setattr(shared, "conceptual_response", lambda *a, **k: shared_called.append(True) or "shared version")
  monkeypatch.setattr(concept_explanation, "_call_pass_two_model", lambda *a, **k: "own inline explanation")

  text, gave_direct_answer = concept_explanation.handle(
    "What is entropy?", _diagnosis("CONCEPTUAL"), "Laws of Thermodynamics", [], None, "sys prompt"
  )

  assert gave_direct_answer is True
  assert text == "own inline explanation"
  assert shared_called == []  # confirms the DRY divergence: does NOT call _shared.conceptual_response


def test_concept_explanation_confirmation_returns_false(monkeypatch):
  monkeypatch.setattr(concept_explanation, "_call_pass_two_model", lambda *a, **k: "general concept explanation")

  text, gave_direct_answer = concept_explanation.handle(
    "So Q = 300 kJ, right?", _diagnosis("CONFIRMATION"),
    "Laws of Thermodynamics", [], {"verdict": "CORRECT", "tier": "semantic"}, "sys prompt"
  )

  assert gave_direct_answer is False


@pytest.mark.parametrize("classification", ["IPS", "IRL"])
def test_concept_explanation_ips_irl_returns_false(monkeypatch, classification):
  monkeypatch.setattr(concept_explanation, "_call_pass_two_model", lambda *a, **k: "full explanation")

  text, gave_direct_answer = concept_explanation.handle(
    "I tried this and got stuck.", _diagnosis(classification), "Laws of Thermodynamics", [], None, "sys prompt"
  )

  assert gave_direct_answer is False


def test_concept_explanation_call_sites_use_max_tokens_above_200():
  """Regression check for testing/issues_to_fix_2026-07-16.md item 1: Concept
  Explanation's own prompt asks for a thorough/in-depth explanation, so its
  call sites need a higher max_tokens than the shared 200 default or responses
  get truncated. Confirms the fix (raising to 400) is present at all 3 sites."""
  import inspect
  source = inspect.getsource(concept_explanation)
  max_tokens_values = [int(v) for v in re.findall(r"max_tokens=(\d+)", source)]
  assert len(max_tokens_values) == 3
  assert all(v > 200 for v in max_tokens_values)
