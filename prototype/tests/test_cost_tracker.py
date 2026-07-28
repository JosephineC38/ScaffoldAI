import pytest

from architecture.testing.cost_tracker import turn_usage, TurnUsageTracker, PRICING_PER_MILLION_TOKENS


def test_reset_clears_state():
  turn_usage.record("gpt-4o-mini", 1000, 500)
  turn_usage.reset()
  assert turn_usage.total_tokens == 0
  assert turn_usage.total_cost_usd == 0.0


def test_record_accumulates_total_tokens():
  turn_usage.record("gpt-4o-mini", 1000, 500)
  turn_usage.record("gpt-4o", 200, 100)
  assert turn_usage.total_tokens == 1000 + 500 + 200 + 100


def test_total_cost_usd_matches_hand_computed_value_single_model():
  turn_usage.record("gpt-4o-mini", 1_000_000, 1_000_000)
  rates = PRICING_PER_MILLION_TOKENS["gpt-4o-mini"]
  expected = rates["input"] + rates["output"]
  assert turn_usage.total_cost_usd == pytest.approx(expected)


def test_total_cost_usd_matches_hand_computed_value_combined_models():
  turn_usage.record("gpt-4o-mini", 1_000_000, 1_000_000)
  turn_usage.record("gpt-4o", 1_000_000, 1_000_000)
  mini = PRICING_PER_MILLION_TOKENS["gpt-4o-mini"]
  full = PRICING_PER_MILLION_TOKENS["gpt-4o"]
  expected = mini["input"] + mini["output"] + full["input"] + full["output"]
  assert turn_usage.total_cost_usd == pytest.approx(expected)


def test_unknown_model_raises_value_error():
  with pytest.raises(ValueError):
    turn_usage.record("some-other-model", 100, 50)


def test_turn_usage_is_a_true_module_level_singleton():
  from architecture.testing.cost_tracker import turn_usage as turn_usage_second_import
  assert turn_usage is turn_usage_second_import


def test_fresh_tracker_starts_empty():
  fresh = TurnUsageTracker()
  assert fresh.total_tokens == 0
  assert fresh.total_cost_usd == 0.0
