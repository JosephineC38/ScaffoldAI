import json

from architecture.modes._shared import _verification_context, _call_pass_two_model


def handle(user_input: str, diagnosis: str, topic: str, conversation_history: list, verification: dict, system_prompt: str, conversation_id: str = "", turn: str = "") -> tuple[str, bool]:
  classification = json.loads(diagnosis).get("classification")

  if classification == "CONCEPTUAL":
    pass_two_prompt = f"""
      topic: {topic}
      diagnostic context: {diagnosis}
      original student input message: {user_input}

      The student is asking a direct factual or definitional question with no problem context to work through. Give a more thorough, in-depth conceptual explanation than a quick definition would provide: cover the underlying principle, explain why it holds, and note where it commonly gets misapplied or misunderstood. Use the diagnostic context's reasoning_gap and misconception fields to calibrate depth and framing, even though there is no problem context here.

      State the explanation directly instead of responding with a question. Do not end your response with a question — if you want to invite further engagement, do it as a statement, not a question.
      """
    response_text = _call_pass_two_model(system_prompt, conversation_history, pass_two_prompt, max_tokens=400, mode="Concept Explanation", conversation_id=conversation_id, turn=turn)
    # ASSUMPTION FLAGGED FOR REVIEW: gave_direct_answer=True here on the
    # reasoning that a bare conceptual question has no student-specific number
    # to leak. Confirm before merging; if wrong, this should be False like the
    # CONFIRMATION and IPS/IRL branches below.
    return response_text, True

  if classification == "CONFIRMATION":
    pass_two_prompt = f"""
      topic: {topic}
      diagnostic context: {diagnosis}
      original student input message: {user_input}
      {_verification_context(verification)}

      The student has already worked through a specific problem and stated a specific result, and is now asking you to confirm whether it's correct. Do NOT confirm or deny their result, and do not state or imply a CORRECT/INCORRECT verdict, even though you have an independent verification result above for your own background awareness only. Instead, explain the underlying concept, law, or sign convention that governs this kind of calculation in general terms, so the student can check their own work against it.

      Do not reveal the diagnosis, and do not state whether their specific number is right or wrong.
      """
    response_text = _call_pass_two_model(system_prompt, conversation_history, pass_two_prompt, max_tokens=400, mode="Concept Explanation", conversation_id=conversation_id, turn=turn)
    return response_text, False

  # IPS / IRL
  pass_two_prompt = f"""
      topic: {topic}
      diagnoistic context (do not reveal this to the student): {diagnosis}
      original student input message: {user_input}

      Using the diagnostic context's reasoning_gap and misconception fields to inform your response, give a full explanation of the relevant concept or misconception in general terms — more than a single Socratic hint or nudge. Do not walk through the student's specific problem, derivation, or numbers, and do not state their specific answer — focus on explaining the underlying principle so the student can apply it themselves.

      Do not reveal the diagnosis or the correct answer.
      """
  response_text = _call_pass_two_model(system_prompt, conversation_history, pass_two_prompt, max_tokens=400, mode="Concept Explanation", conversation_id=conversation_id, turn=turn)
  return response_text, False
