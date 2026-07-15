import json

from architecture.modes import _shared
from architecture.two_pass_engine import _verification_context, _call_pass_two_model


def handle(user_input: str, diagnosis: str, topic: str, conversation_history: list, verification: dict, system_prompt: str) -> tuple[str, bool]:
  classification = json.loads(diagnosis).get("classification")

  if classification == "CONCEPTUAL":
    response_text = _shared.conceptual_response(user_input, diagnosis, topic, conversation_history, system_prompt)
    return response_text, True

  # This mode never takes a direct-verdict path — CONFIRMATION, IPS, and IRL
  # all fall through to the same Socratic, single-hint prompt below, even when
  # verification has a confident CORRECT/INCORRECT verdict on the table.
  pass_two_prompt = f"""
      topic: {topic}
      diagnoistic context (do not reveal this to the student): {diagnosis}
      original student input message: {user_input}
      {_verification_context(verification)}

      Using the diagnostic context above to inform your response, give the student ONE incremental hint or nudge toward the next step — for example, naming the relevant law, equation, or principle they should apply next. Do not give a multi-step scaffold and do not chain together multiple questions; offer a single hint only.

      Do not reveal the diagnosis or the correct answer.
      """

  response_text = _call_pass_two_model(system_prompt, conversation_history, pass_two_prompt)
  return response_text, False
