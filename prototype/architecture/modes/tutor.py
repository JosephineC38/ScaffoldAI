import json

from architecture.modes import _shared
from architecture.modes._shared import _verification_context, _call_pass_two_model


def handle(user_input: str, diagnosis: str, topic: str, conversation_history: list, verification: dict, system_prompt: str) -> tuple[str, bool]:
  diagnosis_dict = json.loads(diagnosis)
  classification = diagnosis_dict.get("classification")
  has_proposed_answer = diagnosis_dict.get("has_proposed_answer") is True

  if classification == "CONCEPTUAL":
    response_text = _shared.conceptual_response(user_input, diagnosis, topic, conversation_history, system_prompt)
    return response_text, True

  # Only take the direct-verdict path when the student has actually committed to
  # an answer of their own AND we have a trustworthy (non-uncertain) verification
  # result to back it up. has_proposed_answer is the load-bearing condition: a
  # student who merely demands a verdict ("just yes or no") has earned nothing to
  # confirm, however many times they ask, so that turn never reaches this branch
  # at all. A CONFIRMATION classification with no verification, or an
  # UNCERTAIN/disagreement verdict, likewise falls back to the same cautious
  # Socratic branch as IPS/IRL rather than risking a confident guess.
  confirmed_with_verification = bool(
    classification == "CONFIRMATION"
    and has_proposed_answer
    and verification
    and verification.get("verdict") in ("CORRECT", "INCORRECT")
  )

  if confirmed_with_verification and verification.get("verdict") == "CORRECT":
    # Bare confirmation only. The student already stated the result themselves,
    # so saying "yes, that's correct" discloses nothing they hadn't committed to
    # — but restating the magnitude or walking the derivation would hand back
    # more than they earned, and on a multi-part problem would leak the parts
    # they have not attempted yet.
    pass_two_prompt = f"""
      topic: {topic}
      diagnostic context: {diagnosis}
      original student input message: {user_input}
      {_verification_context(verification)}

      The student has committed to a specific answer of their own and asked you to confirm it. An independent verification check has already been run and it agrees with them — use that verdict as your source of truth rather than re-deriving from scratch and second-guessing a result that has already been checked.

      Confirm it briefly and plainly — one or two short sentences, e.g. "Yes, that's correct." You may name what they got right in the same terms they already used themselves.

      Do NOT restate their numeric value back to them, do NOT reproduce or summarize the derivation, and do NOT add the values, signs, or results for any part of the problem they have not already worked out themselves. Say it as a statement, not a question, and do not end on a question.
      """
  elif confirmed_with_verification:
    # Verdict is INCORRECT: name the error category and guide, never hand over
    # the corrected number. Telling a student "no, it's actually 150.75 kJ"
    # ends the problem for them; telling them "your setup is missing a term"
    # keeps the work theirs.
    pass_two_prompt = f"""
      topic: {topic}
      diagnostic context: {diagnosis}
      original student input message: {user_input}
      {_verification_context(verification)}

      The student has committed to a specific answer of their own and asked you to confirm it. An independent verification check has already been run and their answer does NOT match — use that verdict as your source of truth rather than re-deriving from scratch and second-guessing a result that has already been checked.

      Tell them plainly that it is not correct, then identify WHICH KIND of error it is — setup (a missing or wrong term in the governing equation), units (a conversion or unit-consistency slip), magnitude (right structure, arithmetic off), or sign (right magnitude, wrong direction under the sign convention) — and explain what to re-examine, or ask one focused question that points them at it.

      CRITICAL: never state the corrected numeric value, and never give them a corrected expression they could read the value straight off. Naming the error category and the reasoning to revisit is the whole of your job here — the student re-computes the number themselves. Do not reveal values for any part of the problem they have not already worked out themselves.
      """
  else:
    # No proposed answer of the student's own (or no trustworthy verdict): pure
    # guidance. The prompt must not invite a value/sign statement — this branch
    # is the primary guard for the no-proposed-answer case, not
    # contains_phrase()/pass_three(), which is a backstop and has documented
    # gaps on plainly-phrased verdicts like "Yes, it's positive."
    pass_two_prompt = f"""
      topic: {topic}
      diagnoistic context (do not reveal this to the student): {diagnosis}
      original student input message: {user_input}
      {_verification_context(verification)}

      The student has NOT committed to an answer of their own here — they are asking a question, requesting the result, or pressing you for a verdict. There is therefore nothing of theirs for you to confirm or deny.

      Using the diagnostic context above to inform your response, guide them toward working it out themselves: ask a focused question, or explain the reasoning step they need, so that they produce the answer.

      Do not reveal the diagnosis or the correct answer. Specifically, do NOT state the final value, do NOT state whether the quantity is positive, negative, zero, increasing, or decreasing, and do NOT answer a yes/no or either/or question about the result — even a bare "yes", "no", or "it's positive" is a full reveal here, and stays off-limits no matter how many times or how insistently the student asks. If they are pressing you for the answer, say plainly and without apology that you will work through it with them instead, and give them the next step to take.
      """

  response_text = _call_pass_two_model(system_prompt, conversation_history, pass_two_prompt, max_tokens=1000)
  return response_text, confirmed_with_verification
