# Minimal per-request token/cost tracker. Restores the `turn_usage` singleton that
# two_pass_engine.py, verification.py, leakage_check.py, and modes/_shared.py already


PRICING_PER_MILLION_TOKENS = {
  "gpt-4o-mini": {"input": 0.15, "output": 0.60},
  "gpt-4o": {"input": 2.50, "output": 10.00},
}


class TurnUsageTracker:
  def __init__(self):
    # holds one tuple per recorded call: (model, prompt_tokens, completion_tokens)
    self._records = [] 

  def reset(self):
    # clears all records
    self._records = []

  def record(self, model: str, prompt_tokens: int, completion_tokens: int):
    # logs on API call's usage
    if model not in PRICING_PER_MILLION_TOKENS:
      raise ValueError(f"Unknown model for cost tracking: {model}")
    self._records.append((model, prompt_tokens, completion_tokens))

  @property
  def total_tokens(self) -> int:
    # sums prompt+completion tokens across every recoreded call
    return sum(prompt + completion for _, prompt, completion in self._records)

  @property
  def total_cost_usd(self) -> float:
    # converts all recorded usage to USD
    total = 0.0
    for model, prompt, completion in self._records:
      rates = PRICING_PER_MILLION_TOKENS[model]
      total += (prompt / 1_000_000) * rates["input"] + (completion / 1_000_000) * rates["output"]
    return total


turn_usage = TurnUsageTracker()
