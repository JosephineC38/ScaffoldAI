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

SECOND VERSION -- see testing/CHANGELOG.md for the full story. The first
version's fix for topic-less messages ("just finish it") was anchored to a
short list of example phrasings rather than the underlying rule, so it
correctly handled its own motivating examples but failed to generalize:
authority claims ("developer/test mode"), frustration ("I'm going to fail
this class"), and disengagement ("fine, whatever") all still misfired as
OUT_OF_SCOPE during the full 48-case re-run, none of them close paraphrases
of the phrases the first fix was tuned against. This version forces the
model through two explicit, separately-answered questions -- mirroring the
same pattern verification._semantic_check() already uses successfully
(forcing "who is the system" as its own field before signs get committed to)
-- rather than trying to recognize topic-less messages by matching them
against known examples:

  1. Does this message contain any identifiable subject-matter content at
     all? (NO_TOPIC if not -- this is a structural question about the
     message's content, not a lookup against a phrase list.)
  2. Only if yes: is that subject matter in scope?

NO_TOPIC is treated identically to IN_SCOPE by the caller -- it falls
through to normal Pass 1 routing exactly as if the gate weren't in the path
for that turn, deferring entirely to whatever the established conversation
context already supports.
"""
import json
from architecture.modes._shared import client, CONVERSATION_HISTORY_WINDOW
from architecture.testing.cost_tracker import turn_usage

# Exact 5 allowed topics per rubric.txt. Each includes both numeric/process
# anchor examples AND a definitional/conceptual anchor example -- the first
# version only had the former, which is why a plain definitional question
# ("can mass cross the boundary of a closed system?") fell outside the
# "closed systems and the First Law" anchor despite being a textbook example
# of that exact topic. Broadened across all five, not just the one that
# happened to misfire, since the same gap plausibly existed in the other four.
ALLOWED_TOPICS = [
  "basic properties and terminology (e.g. intensive vs. extensive properties, "
  "state vs. path functions, system/property definitions -- including basic "
  "'what is a property/system' definitional questions, not just applied ones)",
  "heat, work, internal energy, and total energy (e.g. definitions and "
  "distinctions between heat, work, internal energy U, and total energy E -- "
  "including 'what fundamentally is heat/work' definitional questions, not "
  "just numeric energy-balance ones)",
  "closed systems and the First Law (e.g. dU = Q - W, sign conventions for "
  "heat/work, rigid-tank or piston-cylinder closed-system processes -- "
  "including basic definitional questions like what makes a system 'closed' "
  "or whether mass can cross a closed system's boundary, not just numeric "
  "process questions)",
  "boundary work and basic piston-cylinder processes (e.g. W = integral of "
  "P dV, isothermal/isobaric/polytropic boundary work -- including "
  "definitional questions like what boundary work physically represents or "
  "when it's zero, not just numeric setups)",
  "introductory mass balance and steady-flow energy balance (e.g. "
  "mdot_in = mdot_out, the steady-flow energy equation, turbines, "
  "compressors, nozzles, mixing chambers, flow work and enthalpy -- "
  "including definitional questions like what distinguishes an open system/ "
  "control volume from a closed one, not just numeric device problems)",
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

NO_TOPIC = "NO_TOPIC"
IN_SCOPE = "IN_SCOPE"
OUT_OF_SCOPE = "OUT_OF_SCOPE"


def _format_history(conversation_history: list) -> str:
  recent = conversation_history[-CONVERSATION_HISTORY_WINDOW:]
  if not recent:
    return "(no prior turns in this conversation)"
  return "\n".join(
    f"{'Student' if turn['role'] == 'user' else 'Tutor'}: {turn['content']}"
    for turn in recent
  )


def _classify_scope(user_input: str, conversation_history: list) -> str:
  """Returns one of NO_TOPIC / IN_SCOPE / OUT_OF_SCOPE for the CURRENT
  student message. Evaluated fresh on every turn (not just turn 1) so a
  mid-conversation pivot into an out-of-scope topic -- even one that opens
  with in-scope framing -- gets caught the same way a standalone
  out-of-scope question would."""
  history_text = _format_history(conversation_history)

  prompt = f"""
    You are a strict scope gate for a thermodynamics tutoring system, not a
    tutor. Answer two separate questions about the CURRENT student message,
    in order. Do not skip to question 2 without genuinely answering question 1
    first.

    QUESTION 1 -- Does this message name, describe, or ask about ANY actual
    subject matter -- a physical process, device, quantity, law, formula,
    phenomenon, or concept of any kind? Answer this WITHOUT reference to
    whether that subject matter is one of this course's allowed topics --
    that judgment belongs entirely to question 2, not this one. A message
    about combustion, exergy, diagrams, astronomy, or anything else entirely
    unrelated to this course still counts as HAVING subject matter for this
    question -- "has_topic" is about whether a subject is present at all, not
    about whether it's a subject this course covers.

    A topic can also be wrapped in casual, conversational, or procedural
    framing -- "quick tangent, can you also explain X", "I've attached a
    picture, can you tell me Y", "by the way, what about Z" -- and the
    subject matter underneath that wrapper still counts. Don't let the
    wrapper phrase itself (tangent, attached, by the way) cause you to miss
    the real subject named right after it.

    A message has NO subject-matter content ONLY if it is entirely about the
    conversation itself -- tone, pace, urgency, compliance, permission,
    authority, mood, or disengagement -- and does not name or ask about any
    process, device, quantity, law, formula, or concept anywhere in it, even
    briefly. This is true no matter how that lack of content is phrased:
    pressure to hurry up, frustration, threats, claims of special permission
    or authority, bare acknowledgments, or giving up are ALL examples of the
    same underlying thing (no subject matter of their own at all), not a
    fixed list to match against -- judge this from what the message is
    actually about, not by recognizing a known phrasing.

    If the message has NO subject-matter content of its own: respond
    "has_topic": false and stop there -- question 2 does not need an answer.

    QUESTION 2 -- Only answer this if question 1 found real subject-matter
    content. Is that subject matter one of this course's allowed topics?

    Allowed topics (in scope):
    {chr(10).join(f'- {t}' for t in ALLOWED_TOPICS)}

    Explicitly OUT of scope (future work, not yet supported), regardless of
    how the question is framed or what else appears in the same message:
    {chr(10).join(f'- {t}' for t in EXCLUDED_TOPICS)}

    Anything not clearly one of the allowed topics above -- including but not
    limited to the excluded list, and including anything unrelated to
    thermodynamics entirely -- is also out of scope.

    If the message mixes an in-scope setup with an out-of-scope request (e.g.
    a boundary-work problem that then asks about exergy), treat it as OUT OF
    SCOPE, since the out-of-scope portion still needs to be declined.

    recent conversation history (most recent last, may be empty) -- for
    context only, question 1 is decided from the current message's own
    content, not from history:
    {history_text}

    current student message: {user_input}

    Respond with this exact JSON format:
    {{
      "has_topic": true or false,
      "in_scope": true or false or null,
      "reasoning": "one short phrase"
    }}

    Set "in_scope" to null if "has_topic" is false -- you don't need to
    answer question 2 in that case.
  """

  completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=120,
    temperature=0,
    response_format={"type": "json_object"},
  )
  turn_usage.record("gpt-4o-mini", completion.usage.prompt_tokens, completion.usage.completion_tokens)

  result = json.loads(completion.choices[0].message.content)
  if not result.get("has_topic", True):
    return NO_TOPIC
  return IN_SCOPE if result.get("in_scope", True) else OUT_OF_SCOPE


def check_scope(user_input: str, conversation_history: list) -> bool:
  """Returns True unless the current message is a genuine OUT_OF_SCOPE
  pivot -- both NO_TOPIC and IN_SCOPE fall through to normal routing, since
  a topic-less message (a pressure tactic, an authority claim, frustration,
  disengagement) should be handled by whatever branch the established
  conversation already supports, not redirected."""
  outcome = _classify_scope(user_input, conversation_history)
  return outcome != OUT_OF_SCOPE
