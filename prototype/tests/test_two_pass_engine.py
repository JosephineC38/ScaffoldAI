import json
import logging
import pytest

import architecture.two_pass_engine as tpe
from architecture.two_pass_engine import (
  has_problem_context, generate_response, _extract_verification_inputs,
  canonicalize_topic,
)
from architecture.config.thermo_topics import TOPICS
from architecture.config.topic_reference import (
  TOPIC_REFERENCE, DEFAULT_REFERENCE, get_reference,
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


# --- canonicalize_topic ------------------------------------------------------
# pass_one's topic is a soft prompt instruction, so the model returns
# word-order/casing variants that used to miss get_reference()'s exact-match
# lookup and silently drop that topic's reference material. These tests are
# the generalization check: they cover the two variants actually observed in
# the transcript corpus AND synthetic reorderings of other TOPICS entries
# that have never appeared in logs, since a fix validated only against the
# cases that revealed the bug is what has repeatedly failed to generalize on
# this codebase (testing/session_summary_2026-07-30.md §9).

def test_canonicalize_topic_is_identity_on_every_exact_topics_entry():
  for topic in TOPICS:
    assert canonicalize_topic(topic) == topic


@pytest.mark.parametrize("raw,expected", [
  # The variant measured at 44/142 turns across testing/transcripts{,_v2}/
  # and 20/40 runs in the before-measurement -- word order swapped.
  ("Work, Heat, and Energy Transfer", "Heat, Work, and Energy Transfer"),
  # Synthetic reorderings of OTHER entries, never observed in logs -- these
  # are the actual generalization check.
  ("Closed vs Open Systems", "Open vs Closed Systems"),
  ("Phase Changes and Properties of Pure Substances",
   "Properties of Pure Substances and Phase Changes"),
  ("Real Gases and Equations of State", "Equations of State and Real Gases"),
  ("Exergy and Entropy", "Entropy and Exergy"),
  ("Thermochemistry and Combustion", "Combustion and Thermochemistry"),
])
def test_canonicalize_topic_matches_word_order_variants(raw, expected):
  assert canonicalize_topic(raw) == expected


@pytest.mark.parametrize("raw,expected", [
  ("heat, work, and energy transfer", "Heat, Work, and Energy Transfer"),
  ("LAWS OF THERMODYNAMICS", "Laws of Thermodynamics"),
  ("  Thermodynamic   Cycles  ", "Thermodynamic Cycles"),
  ("Open vs. Closed Systems", "Open vs Closed Systems"),          # extra period
  ("Entropy & Exergy", "Entropy and Exergy"),                     # '&' -> dropped, 'and' remains in canonical
])
def test_canonicalize_topic_normalizes_case_whitespace_and_punctuation(raw, expected):
  assert canonicalize_topic(raw) == expected


@pytest.mark.parametrize("raw", [
  "Heat",                  # observed 2/142 in the corpus -- a bare fragment
  "Work",
  "Energy Transfer",       # strict subset of a real entry
  "Psychrometrics and Combustion",   # words from two different entries
  "Rankine Cycle Analysis",
  "",
  "   ",
  None,
  123,
])
def test_canonicalize_topic_returns_none_for_unrecognized_labels(raw):
  """Subsets and junk deliberately do NOT match. Guessing which topic a bare
  'Heat' meant would trade a silent missing-reference bug for a silent
  wrong-reference bug; these return None so the caller logs and falls back."""
  assert canonicalize_topic(raw) is None


def test_canonicalize_topic_result_always_hits_real_reference_material():
  """The property that actually matters: anything canonicalize_topic matches
  is guaranteed to retrieve real material, never DEFAULT_REFERENCE."""
  for raw in ["Work, Heat, and Energy Transfer", "Closed vs Open Systems",
              "LAWS OF THERMODYNAMICS", "Exergy and Entropy"]:
    canonical = canonicalize_topic(raw)
    assert get_reference(canonical) != DEFAULT_REFERENCE
    assert get_reference(canonical) == TOPIC_REFERENCE[canonical]


def test_pass_one_canonicalizes_before_returning(monkeypatch, make_openai_response):
  """Wiring check: the raw label must not survive out of pass_one, since
  every downstream consumer (get_reference, the pass_two prompt, transcript
  logging) reads whatever pass_one returns."""
  content = json.dumps({
    "topic": "Work, Heat, and Energy Transfer",
    "classification": "IRL",
    "reasoning_gap": "mocked",
    "misconception": None,
  })
  monkeypatch.setattr(tpe.client.chat.completions, "create",
                      lambda **kw: make_openai_response(content))

  topic, _ = tpe.pass_one("some student message", [])

  assert topic == "Heat, Work, and Energy Transfer"


def test_pass_one_logs_warning_and_keeps_raw_label_when_unrecognized(
    monkeypatch, make_openai_response, caplog):
  """Unrecognized labels keep the old student-visible behavior (fall through
  to DEFAULT_REFERENCE) but must no longer do it silently."""
  content = json.dumps({
    "topic": "Heat",
    "classification": "IRL",
    "reasoning_gap": "mocked",
    "misconception": None,
  })
  monkeypatch.setattr(tpe.client.chat.completions, "create",
                      lambda **kw: make_openai_response(content))

  with caplog.at_level(logging.WARNING, logger="architecture.two_pass_engine"):
    topic, _ = tpe.pass_one("a message about heating a tank", [])

  assert topic == "Heat"                                   # unchanged fallback
  assert get_reference(topic) == DEFAULT_REFERENCE         # unchanged behavior
  assert "unrecognized topic label" in caplog.text         # but now visible
  assert "'Heat'" in caplog.text
  assert "a message about heating a tank" in caplog.text   # traceable to a turn


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
  # check_scope() calls out to architecture.modes._shared.client -- a
  # separate OpenAI client instance from tpe.client, so patching the create()
  # above doesn't cover it. These tests are about post-classification wiring,
  # not the scope gate itself (see test_generate_response_scope_gate.py for
  # that), so always report in-scope here.
  monkeypatch.setattr(tpe, "check_scope", lambda user_input, conversation_history: True)


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


# --- proposed_value threading and fail-safe ----------------------------------

@pytest.mark.parametrize("raw,expected", [
  ("215.4 kJ", "215.4 kJ"),
  ("  -94.6 kJ  ", "-94.6 kJ"),
  ("positive", "positive"),
  (215.4, "215.4"),                 # model sometimes emits a bare JSON number
  (None, None),                     # JSON null
  ("", None),
  ("   ", None),
  ("null", None),                   # string spelling of null
  ("N/A", None),
  (True, None),                     # bool is not a claim
  ({"value": 1}, None),             # malformed shape
])
def test_clean_proposed_value(raw, expected):
  assert tpe._clean_proposed_value(raw) == expected


def _mock_pass_one_with_proposal(monkeypatch, make_openai_response, has_proposed, proposed_value):
  content = json.dumps({
    "topic": "Laws of Thermodynamics",
    "classification": "CONFIRMATION",
    "has_proposed_answer": has_proposed,
    "proposed_value": proposed_value,
    "reasoning_gap": "mocked",
    "misconception": None,
  })
  monkeypatch.setattr(tpe.client.chat.completions, "create",
                      lambda **k: make_openai_response(content, prompt_tokens=50, completion_tokens=20))
  monkeypatch.setattr(tpe, "check_scope", lambda user_input, conversation_history: True)


def test_generate_response_passes_proposed_value_into_verify_answer(monkeypatch, make_openai_response):
  """The claimed value handed to verify_answer must be pass_one's extracted
  proposed_value, not anything re-derived from the raw message."""
  _mock_pass_one_with_proposal(monkeypatch, make_openai_response, True, "215.4 kJ")
  captured = {}

  def fake_verify(problem_statement, student_answer, topic, proposed_value):
    captured["proposed_value"] = proposed_value
    return {"verdict": "CORRECT", "tier": "semantic", "correct_value": "215.4 kJ", "reasoning": "r"}

  monkeypatch.setattr(tpe, "verify_answer", fake_verify)
  monkeypatch.setattr(tpe, "MODE_HANDLERS", {**tpe.MODE_HANDLERS,
                      "Hint-only": lambda *a, **k: ("stub", False)})

  generate_response("I calculated Q = 215.4 kJ using cv = 0.718 kJ/kg·K, right?", [], "Hint-only")

  assert captured["proposed_value"] == "215.4 kJ"


@pytest.mark.parametrize("bad_value", [None, "", "null"])
def test_generate_response_skips_verification_when_proposed_value_unusable(
    monkeypatch, make_openai_response, bad_value):
  """Fail safe: has_proposed_answer true but no usable proposed_value must NOT
  fall back to regex extraction (the bug being fixed) -- it must skip
  verification entirely so the turn routes Socratic."""
  _mock_pass_one_with_proposal(monkeypatch, make_openai_response, True, bad_value)

  def exploding_verify(*a, **k):
    raise AssertionError("verify_answer must not run without a usable proposed_value")

  monkeypatch.setattr(tpe, "verify_answer", exploding_verify)
  captured = {}

  def stub_handler(user_input, diagnosis, topic, conversation_history, verification, system_prompt):
    captured["verification"] = verification
    return "stub", False

  monkeypatch.setattr(tpe, "MODE_HANDLERS", {**tpe.MODE_HANDLERS, "Hint-only": stub_handler})

  _, _, diagnostics = generate_response("So is it 45 kJ?", [], "Hint-only")

  assert captured["verification"] is None
  assert diagnostics.get("verification_verdict") is None
