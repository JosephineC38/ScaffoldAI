import sys
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[1] / "architecture"))

from two_pass_engine import pass_one, pass_two  # noqa: E402

# phrases that indicate the model deflected into a guiding question
# instead of directly answering a conceptual ask
SCAFFOLD_PHRASES = [
  "can you think",
  "let's explore",
  "what do you think",
  "have you considered",
  "let's think about",
  "can you tell me",
]

CONCEPTUAL_CASES = [
  "What is the first law of thermodynamics?",
  "What is entropy?",
  "What is the equation for the Carnot efficiency?",
]

CONTROL_CASE = (
  "I'm doing a piston-cylinder problem where the gas expands and I calculated "
  "the work as -500 J, but I think it should be positive since the gas is doing "
  "work on the surroundings. What am I doing wrong?"
)


def run_case(user_input: str):
  topic, diagnosis = pass_one(user_input)
  classification = json.loads(diagnosis).get("classification")
  response = pass_two(user_input, diagnosis, topic, [])
  return classification, response


def check_conceptual(user_input: str) -> bool:
  classification, response = run_case(user_input)
  response_lower = response.lower()

  failures = []
  if classification != "CONCEPTUAL":
    failures.append(f"expected classification CONCEPTUAL, got {classification}")
  if response.strip().endswith("?"):
    failures.append("response ends in a question instead of an answer")
  hit_phrases = [p for p in SCAFFOLD_PHRASES if p in response_lower]
  if hit_phrases:
    failures.append(f"response contains scaffolding phrase(s): {hit_phrases}")

  status = "PASS" if not failures else "FAIL"
  print(f"[{status}] {user_input!r}")
  print(f"  classification: {classification}")
  print(f"  response: {response}")
  for f in failures:
    print(f"  - {f}")
  print()

  return not failures


def check_control(user_input: str) -> bool:
  classification, response = run_case(user_input)

  # sanity check only: an execution-error question should not be misrouted
  # into the direct-answer path meant for CONCEPTUAL asks
  ok = classification != "CONCEPTUAL"
  status = "PASS" if ok else "FAIL"
  print(f"[{status}] (control) {user_input!r}")
  print(f"  classification: {classification}")
  print(f"  response: {response}")
  print()

  return ok


if __name__ == "__main__":
  results = [check_conceptual(q) for q in CONCEPTUAL_CASES]
  results.append(check_control(CONTROL_CASE))

  if all(results):
    print("All checks passed.")
    sys.exit(0)
  else:
    print(f"{results.count(False)} of {len(results)} checks failed.")
    sys.exit(1)
