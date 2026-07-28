# Minimal per-request token/cost tracker. Restores the `turn_usage` singleton that
# two_pass_engine.py, verification.py, leakage_check.py, and modes/_shared.py already
# import and call (.reset()/.record()/.total_tokens/.total_cost_usd) but that was never
# actually added to the repo.

# Rates are USD per 1M tokens. gpt-4o-mini rate matches the in-code comments already in
# pass_one()/pass_three(); gpt-4o rate should be re-checked against
# https://openai.com/api/pricing/ before treating totals as real budget figures.
PRICING_PER_MILLION_TOKENS = {
  "gpt-4o-mini": {"input": 0.15, "output": 0.60},
  "gpt-4o": {"input": 2.50, "output": 10.00},
}


class TurnUsageTracker:
  def __init__(self):
    self._records = []

  def reset(self):
    self._records = []

  def record(self, model: str, prompt_tokens: int, completion_tokens: int):
    if model not in PRICING_PER_MILLION_TOKENS:
      raise ValueError(f"Unknown model for cost tracking: {model}")
    self._records.append((model, prompt_tokens, completion_tokens))

  @property
  def total_tokens(self) -> int:
    return sum(prompt + completion for _, prompt, completion in self._records)

  @property
  def total_cost_usd(self) -> float:
    total = 0.0
    for model, prompt, completion in self._records:
      rates = PRICING_PER_MILLION_TOKENS[model]
      total += (prompt / 1_000_000) * rates["input"] + (completion / 1_000_000) * rates["output"]
    return total


turn_usage = TurnUsageTracker()
