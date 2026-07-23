"""Reusable helper for appending per-call OpenAI cost/latency rows to
testing/cost_log.csv. Append-only, separate from testing/results_log.csv
(different purpose/schema — never write there from here).
"""
import csv
from datetime import datetime
from pathlib import Path

COST_LOG_PATH = Path(__file__).resolve().parents[2] / "testing" / "cost_log.csv"

FIELDNAMES = [
  "timestamp", "conversation_id", "turn", "mode", "call_site",
  "model", "prompt_tokens", "completion_tokens", "latency_ms",
]


def log_cost_event(call_site: str, model: str, response, elapsed_seconds: float,
                    mode: str = "", conversation_id: str = "", turn: str = "",
                    csv_path: Path = COST_LOG_PATH) -> None:
  """Append one row capturing token usage + latency for a single OpenAI call.
  Skips logging (without raising) if the response has no usable usage field —
  e.g. a streaming response — since the call itself already happened and
  missing usage data isn't a reason to fail it."""
  usage = getattr(response, "usage", None)
  if usage is None:
    return
  prompt_tokens = getattr(usage, "prompt_tokens", None)
  completion_tokens = getattr(usage, "completion_tokens", None)
  if prompt_tokens is None or completion_tokens is None:
    return

  csv_path.parent.mkdir(parents=True, exist_ok=True)
  file_exists = csv_path.is_file()
  with open(csv_path, "a", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
    if not file_exists:
      writer.writeheader()
    writer.writerow({
      "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
      "conversation_id": conversation_id,
      "turn": turn,
      "mode": mode,
      "call_site": call_site,
      "model": model,
      "prompt_tokens": prompt_tokens,
      "completion_tokens": completion_tokens,
      "latency_ms": round(elapsed_seconds * 1000, 2),
    })
