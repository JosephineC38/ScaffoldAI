import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from architecture import prompt_builder
from architecture.config.thermo_topics import TOPICS
from architecture.leakage_check import contains_phrase, pass_three
from architecture.verification import verify_answer, contains_stated_answer

dotenv_path = Path(__file__).parents[2] / ".env"
load_dotenv(dotenv_path)

API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)

PASS_ONE_HISTORY_WINDOW = 8  # last N messages (not exchanges) of conversation_history


def _format_history_for_pass_one(conversation_history: list) -> str:
  recent = conversation_history[-PASS_ONE_HISTORY_WINDOW:]
  if not recent:
    return "(no prior turns in this conversation)"
  return "\n".join(
    f"{'Student' if turn['role'] == 'user' else 'Tutor'}: {turn['content']}"
    for turn in recent
  )


VERIFICATION_LOOKBACK = 6  # last N messages of conversation_history to scan for prior problem context


def _extract_verification_inputs(user_input: str, conversation_history: list) -> tuple:
  """Build (problem_statement, student_answer) for verify_answer using only
  student-authored text — never the tutor's own prior turns — so verification
  can't inherit drift introduced by the AI's own earlier (possibly wrong)
  responses in this conversation. student_answer is always the current
  message; problem_statement is prior numeric student turns for context."""
  recent_student_turns = [
    turn["content"] for turn in conversation_history[-VERIFICATION_LOOKBACK:]
    if turn["role"] == "user" and any(c.isdigit() for c in turn["content"])
  ]
  problem_statement = " ".join(recent_student_turns) if recent_student_turns else user_input
  return problem_statement, user_input


def pass_one(user_input: str, conversation_history: list):
  history_text = _format_history_for_pass_one(conversation_history)

  pass_one_prompt = f"""
    recent conversation history (most recent last, may be empty if this is the first message):
    {history_text}

    student input: {user_input}

    Respond with this exact JSON format:
    {{
      "topic": "one of: {', '.join(TOPICS)}",
      "classification": "IPS", "IRL", "CONCEPTUAL", or "CONFIRMATION"
      "reasoning_gap": "brief description of what the student is missing/asking",
      "misconception": "specific misconception if one exists, otherwise null"
    }}

    Classification rules:
    - IPS: student has encountered this concept before but is making an execution error
    - IRL: concept is new to the student
    - CONCEPTUAL: student is asking for a definition, law, formula, or terminology directly, with no problem context, numeric values, or reference to their own attempt
    - CONFIRMATION: the student has already worked through a specific problem (in this message or earlier in the conversation history) and has a specific result on the table, and is now asking for a verdict on it — e.g. "so delta U = 300 J, right?", "is that correct?", "can you just tell me if I'm right or wrong?". Use the conversation history to check whether a derivation/result was already stated before classifying this way; a bare "is that right?" with no prior derivation in view is not enough on its own.


    Do NOT include the correct answer. Respond only with structured diagnostic. Your output will not be shown to the student
    """

  pass_one_analysis = client.chat.completions.create(
    model = "gpt-4o-mini", # $0.15/million input tokens, $0.60/million output tokens
    messages=[
      {"role": "user",
       "content": pass_one_prompt}
    ],
    max_tokens=200,
    temperature=0.1, # low creativity output
    response_format={"type": "json_object"},
  )

  diagnosis = json.loads(pass_one_analysis.choices[0].message.content)
  topic = diagnosis.pop("topic")

  return topic, json.dumps(diagnosis)

# _call_pass_two_model/_verification_context now live in architecture.modes._shared
# (mode-neutral, imported by both this module and the mode handler files) rather
# than here, so this module and the mode handler files no longer import from each
# other in both directions — see architecture/modes/_shared.py.
from architecture.modes._shared import _call_pass_two_model, _verification_context
from architecture.modes import tutor
from architecture.modes import hint_only
from architecture.modes import concept_explanation

MODE_HANDLERS = {
  "Tutor": tutor.handle,
  "Hint-only": hint_only.handle,
  "Concept Explanation": concept_explanation.handle,
}

def pass_two(user_input: str, pass_one_diagnosis: str, topic: str, conversation_history: list, mode: str, verification: dict = None):
  system_prompt = prompt_builder.prompt_builder()
  handler = MODE_HANDLERS.get(mode)
  if handler is None:
    raise NotImplementedError(f"Mode '{mode}' not yet implemented")
  return handler(user_input, pass_one_diagnosis, topic, conversation_history, verification, system_prompt)

def generate_response(user_input: str, conversation_history, mode: str):
  topic, diagnosis = pass_one(user_input, conversation_history)
  classification = json.loads(diagnosis).get("classification")

  # Run answer verification whenever the student appears to have a specific
  # result on the table — primarily driven by the CONFIRMATION classification,
  # with an independent heuristic backstop (contains_stated_answer) in case
  # classification misses it. Deliberately does not pass conversation_history
  # into verify_answer itself — see _extract_verification_inputs.
  verification = None
  if classification == "CONFIRMATION" or contains_stated_answer(user_input):
    problem_statement, student_answer = _extract_verification_inputs(user_input, conversation_history)
    verification = verify_answer(problem_statement, student_answer, topic)

  system_response, gave_direct_answer = pass_two(user_input, diagnosis, topic, conversation_history, mode, verification)

  if not gave_direct_answer and contains_phrase(system_response):
    system_response = pass_three(system_response, topic)

  diagnostics = json.loads(diagnosis)
  if verification:
    diagnostics["verification_verdict"] = verification.get("verdict")
    diagnostics["verification_tier"] = verification.get("tier")

  return system_response, topic, diagnostics
