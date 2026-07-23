"""Reusable helper for appending per-response leakage-detector rows to
testing/leakage_eval_log.csv. Append-only, same convention as cost_log.py.

Unlike cost_log.py, this log intentionally stores the full response text —
precision/recall evaluation of the detectors themselves requires being able
to read what was actually flagged.
"""
import csv
import json
from datetime import datetime
from pathlib import Path

LEAKAGE_EVAL_LOG_PATH = Path(__file__).resolve().parents[2] / "testing" / "leakage_eval_log.csv"

FIELDNAMES = [
  "timestamp", "conversation_id", "turn", "mode",
  "phrase_flagged", "phrase_matches",
  "numeric_flagged", "numeric_matches",
  "response_text",
]


def log_leakage_eval(conversation_id: str, turn: str, mode: str,
                      phrase_flagged: bool, phrase_matches: list,
                      numeric_flagged: bool, numeric_matches: list,
                      response_text: str, csv_path: Path = LEAKAGE_EVAL_LOG_PATH) -> None:
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
      "phrase_flagged": phrase_flagged,
      "phrase_matches": json.dumps(phrase_matches),
      "numeric_flagged": numeric_flagged,
      "numeric_matches": json.dumps(numeric_matches),
      "response_text": response_text,
    })
