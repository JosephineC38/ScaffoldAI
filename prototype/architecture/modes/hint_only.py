import json

from architecture.modes import _shared
from architecture.modes._shared import _verification_context, _call_pass_two_model


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

      Never affirm, confirm, deny, or hedge-affirm whether the student's stated answer, approach, formula choice, or reasoning is correct — even when they ask you directly ("is that right?", "am I on the right track?", "that's right, isn't it?"). This applies to soft or hedged phrasing just as much as a direct verdict, and it applies equally to confirming their approach/formula as to confirming their final numeric answer — praising the method ("you used the right formula," "that's the correct equation for this") is just as much a verdict as praising the result. Banned phrasing includes (not limited to): "yes, that's correct," "that's right," "that seems correct," "you're on the right track," "that sounds about right," "you used the right formula," "that's the correct approach," "close," "not quite," "that's not right," or a bare "yes"/"no" in answer to a correctness question. Instead, name or restate the relevant formula/principle neutrally, without characterizing whether the student's own use of it was right or wrong. If the student asks for a yes/no verdict on their own answer, do not answer that yes/no question at all — redirect with the same single incremental hint or guiding question instead of confirming, denying, or hedging.

      Do not reveal the diagnosis or the correct answer.
      """

  response_text = _call_pass_two_model(system_prompt, conversation_history, pass_two_prompt, max_tokens=1000)
  return response_text, False
