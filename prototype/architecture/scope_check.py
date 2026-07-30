"""
Deterministic topic-scope gate, run in front of Pass 1 classification for
every turn. Confirmed via full-codebase search that no scope-boundary check
previously existed anywhere in the pipeline (wired or unwired) -- the only
prior scope-related text was the advisory `scope_enforcement` component in
system_prompt_components.json, which (a) is phrased around "outside the
domain of thermodynamics" rather than this course's specific 5-topic
curriculum scope, and (b) is only ever a soft instruction handed to the same
model that's also told to answer conceptual questions directly, so it erodes
under exactly the branches (CONCEPTUAL, IRL) that need to hold it.

This module makes the SCOPE DETERMINATION with a model call (a binary
judgment call, same category of task as Pass 1's own IPS/IRL/CONCEPTUAL/
CONFIRMATION classification), but the ACTION taken on that determination is
deterministic code: if out of scope, the caller returns REDIRECT_MESSAGE
verbatim and skips Pass 1/Pass 2/verification entirely. There is no free
generation involved in producing the redirect text itself.
"""
import json
from architecture.modes._shared import client, CONVERSATION_HISTORY_WINDOW
from architecture.testing.cost_tracker import turn_usage

# Exact 5 allowed topics per rubric.txt, each with a few concrete anchor
# examples -- the bare category labels alone (e.g. "basic properties and
# terminology") were found during validation to be too abstract for the
# gpt-4o-mini scope-check call to reliably pattern-match specific student
# questions onto (e.g. it didn't recognize "intensive vs. extensive
# property" as falling under that label without an example spelling it out).
ALLOWED_TOPICS = [
  "basic properties and terminology (e.g. intensive vs. extensive properties, "
  "state vs. path functions, system/property definitions)",
  "heat, work, internal energy, and total energy (e.g. definitions and "
  "distinctions between heat, work, internal energy U, and total energy E)",
  "closed systems and the First Law (e.g. dU = Q - W, sign conventions for "
  "heat/work, rigid-tank or piston-cylinder closed-system processes)",
  "boundary work and basic piston-cylinder processes (e.g. W = integral of "
  "P dV, isothermal/isobaric/polytropic boundary work)",
  "introductory mass balance and steady-flow energy balance (e.g. "
  "mdot_in = mdot_out, the steady-flow energy equation, turbines, "
  "compressors, nozzles, mixing chambers, flow work and enthalpy)",
]

# Named future-work exclusions per rubric.txt -- listed explicitly in the
# scope-check prompt so near-miss cases (e.g. "exergy" specifically) aren't
# left to the model to infer are out of bounds.
EXCLUDED_TOPICS = [
  "psychrometrics",
  "combustion and thermochemistry",
  "detailed real-gas models (e.g. Redlich-Kwong, other non-ideal equations of state)",
  "exergy",
  "advanced cycles (e.g. full Rankine/Brayton/Carnot cycle analysis, cycle efficiency)",
  "diagram or image interpretation",
]

REDIRECT_MESSAGE = (
  "That topic is outside the current scope of this tutoring system. Right now "
  "this tutor covers: basic properties and terminology; heat, work, internal "
  "energy, and total energy; closed systems and the First Law; boundary work "
  "and basic piston-cylinder processes; and introductory mass balance and "
  "steady-flow energy balance. Let's refocus on your current thermodynamics "
  "problem within those areas."
)


def _format_history(conversation_history: list) -> str:
  recent = conversation_history[-CONVERSATION_HISTORY_WINDOW:]
  if not recent:
    return "(no prior turns in this conversation)"
  return "\n".join(
    f"{'Student' if turn['role'] == 'user' else 'Tutor'}: {turn['content']}"
    for turn in recent
  )


def check_scope(user_input: str, conversation_history: list) -> bool:
  """Returns True if the CURRENT student message is in scope, False otherwise.
  Evaluated fresh on every turn (not just turn 1) so a mid-conversation pivot
  into an out-of-scope topic -- even one that opens with in-scope framing --
  gets caught the same way a standalone out-of-scope question would."""
  history_text = _format_history(conversation_history)

  prompt = f"""
    You are a strict scope gate for a thermodynamics tutoring system, not a tutor.
    Your only job is to decide whether the CURRENT student message asks about
    (or requires engaging with) a topic inside this course's allowed scope.

    Allowed topics (in scope):
    {chr(10).join(f'- {t}' for t in ALLOWED_TOPICS)}

    Explicitly OUT of scope (future work, not yet supported), regardless of how
    the question is framed or what else appears in the same message:
    {chr(10).join(f'- {t}' for t in EXCLUDED_TOPICS)}

    Anything not clearly one of the allowed topics above -- including but not
    limited to the excluded list, and including anything unrelated to
    thermodynamics entirely -- is also out of scope.

    If the message mixes an in-scope setup with an out-of-scope request (e.g.
    a boundary-work problem that then asks about exergy), treat it as OUT OF
    SCOPE, since the out-of-scope portion still needs to be declined.

    The current message often won't restate a topic at all -- short
    follow-ups, requests to continue/finish/hurry up, or pressure tactics
    ("just give me the number", "finish it", "come on") don't introduce any
    topic of their own. In that case, use the recent conversation history to
    determine what topic is actually being discussed: if the established
    topic from history is in scope and the current message doesn't pivot to
    a new topic, treat the current message as IN SCOPE too -- don't flag a
    topic-less continuation as out of scope just because it doesn't restate
    the topic by name. Only mark a message out of scope for introducing a
    new topic (like MT03 turn 2's "can you also explain combustion
    efficiency", or SC04's mid-problem pivot into exergy), not for being a
    short reply that leans on established context.

    recent conversation history (most recent last, may be empty):
    {history_text}

    current student message: {user_input}

    Respond with this exact JSON format:
    {{
      "in_scope": true or false,
      "reasoning": "one short phrase"
    }}
  """

  completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=100,
    temperature=0,
    response_format={"type": "json_object"},
  )
  turn_usage.record("gpt-4o-mini", completion.usage.prompt_tokens, completion.usage.completion_tokens)

  result = json.loads(completion.choices[0].message.content)
  return bool(result.get("in_scope", True))
