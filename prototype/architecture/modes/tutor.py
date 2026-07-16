import json

from architecture.modes import _shared
from architecture.modes._shared import _verification_context, _call_pass_two_model


def handle(user_input: str, diagnosis: str, topic: str, conversation_history: list, verification: dict, system_prompt: str) -> tuple[str, bool]:
  classification = json.loads(diagnosis).get("classification")

  if classification == "CONCEPTUAL":
    response_text = _shared.conceptual_response(user_input, diagnosis, topic, conversation_history, system_prompt)
    return response_text, True

  # Only take the direct-verdict path when we have a trustworthy (non-uncertain)
  # verification result to back it up. A CONFIRMATION classification with no
  # verification, or an UNCERTAIN/disagreement verdict, falls back to the same
  # cautious Socratic branch as IPS/IRL rather than risking a confident guess.
  confirmed_with_verification = (
    classification == "CONFIRMATION" and verification and verification.get("verdict") in ("CORRECT", "INCORRECT")
  )

  if confirmed_with_verification:
    pass_two_prompt = f"""
      topic: {topic}
      diagnostic context: {diagnosis}
      original student input message: {user_input}
      {_verification_context(verification)}

      The student has already worked through a specific problem and stated a specific result, and is now asking you to confirm whether it's correct. An independent verification check has already been run — use its verdict above as your primary source of truth rather than re-deriving from scratch and second-guessing a result that's already been checked.

      Give a clear, direct verdict: tell them plainly whether their result is correct or incorrect, and state the correct value if theirs was wrong. State this directly instead of responding with a question. Do not end your response with a question — if you want to invite further engagement, do it as a statement, not a question.
      """
  else:
    pass_two_prompt = f"""
      topic: {topic}
      diagnoistic context (do not reveal this to the student): {diagnosis}
      original student input message: {user_input}
      {_verification_context(verification)}

      Using the diagnostic context above to inform your response, generate a response to help guide the student.

      Do not reveal the diagnosis or the correct answer.
      """

  response_text = _call_pass_two_model(system_prompt, conversation_history, pass_two_prompt, max_tokens=200)
  return response_text, confirmed_with_verification
