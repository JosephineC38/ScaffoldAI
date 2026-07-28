import pytest

from architecture.config.leakage_patterns import (
  ALL_PHRASES, DIRECT_ANSWER_DECLARATIONS, THERMO_SPECIFIC,
  CALCULATION_COMPLETION, FORMULA_REVELATION,
)
from architecture.leakage_check import contains_phrase, pass_three
from architecture.testing.cost_tracker import turn_usage


@pytest.mark.parametrize("phrase", ALL_PHRASES)
def test_contains_phrase_detects_every_configured_phrase(phrase):
  assert contains_phrase(f"A sentence containing {phrase} somewhere in it.")


def test_contains_phrase_is_case_insensitive():
  assert contains_phrase("THE ANSWER IS 42")
  assert contains_phrase("The Answer Is 42")


def test_contains_phrase_returns_false_with_no_match():
  assert not contains_phrase("Can you tell me what direction heat flows in this process?")


@pytest.mark.parametrize("text", [
  "The rate at which the work done is dependent on the pressure differs by process.",
  "We are using the equation for entropy change in this general discussion.",
  "Applying the formula here is a separate step from evaluating it.",
  "Therefore, we should think carefully about what direction energy moves.",
])
def test_contains_phrase_known_false_positives_still_present(text):
  """Documents the still-open issue (testing/issues_to_fix_2026-07-16.md item 4):
  these phrases are generic enough to false-positive on non-leaking text. This
  test asserts the CURRENT (buggy) behavior so a future fix is a deliberate,
  visible change to this test rather than a silent regression."""
  assert contains_phrase(text)


def test_all_phrases_is_the_union_of_the_four_categories():
  assert ALL_PHRASES == (
    DIRECT_ANSWER_DECLARATIONS + THERMO_SPECIFIC + CALCULATION_COMPLETION + FORMULA_REVELATION
  )


def test_calculation_completion_has_a_known_duplicate_entry():
  """Newly noticed: "we find" appears twice in CALCULATION_COMPLETION. Harmless
  today (list, not set, so contains_phrase()'s behavior is unaffected), but
  flagged explicitly rather than silently tolerated."""
  assert CALCULATION_COMPLETION.count("we find") == 2


def test_pass_three_calls_model_and_records_usage(monkeypatch, make_openai_response):
  captured = {}

  def fake_create(*, model, messages, max_tokens, temperature):
    captured["model"] = model
    captured["prompt"] = messages[0]["content"]
    captured["max_tokens"] = max_tokens
    return make_openai_response("Rewritten Socratic response.", prompt_tokens=120, completion_tokens=40)

  import architecture.leakage_check as leakage_check
  monkeypatch.setattr(leakage_check.client.chat.completions, "create", fake_create)

  result = leakage_check.pass_three("The answer is 300 kJ.", "Laws of Thermodynamics")

  assert result == "Rewritten Socratic response."
  assert captured["model"] == "gpt-4o-mini"
  assert "The answer is 300 kJ." in captured["prompt"]
  assert "Laws of Thermodynamics" in captured["prompt"]
  assert turn_usage.total_tokens == 160
