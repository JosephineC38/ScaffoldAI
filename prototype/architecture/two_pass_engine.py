import os
import re
import json
import logging
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from architecture import prompt_builder
from architecture.config.thermo_topics import TOPICS
from architecture.leakage_check import contains_phrase, pass_three
from architecture.verification import verify_answer, contains_proposed_answer
from architecture.testing.cost_tracker import turn_usage
from architecture.scope_check import check_scope, REDIRECT_MESSAGE

dotenv_path = Path(__file__).parents[2] / ".env"
load_dotenv(dotenv_path)

API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)

logger = logging.getLogger(__name__)

from architecture.modes._shared import CONVERSATION_HISTORY_WINDOW


# --- Topic canonicalization ------------------------------------------------
# pass_one's "topic" is a soft prompt instruction ("one of: {TOPICS}"), not a
# constrained enum, so the model returns semantically-identical labels with
# different surface text — most commonly a word-order swap ("Work, Heat, and
# Energy Transfer" for "Heat, Work, and Energy Transfer"). get_reference()
# does an exact-match dict lookup, so every such variant silently fell back
# to DEFAULT_REFERENCE and the verification tier lost that topic's real
# formulas — including, for that specific pair, the by-system sign-convention
# text. Measured at 46/133 non-scope turns (~35%) across
# testing/transcripts{,_v2}/ and 25/40 runs in
# testing/topic_canonicalization_before_2026-08-03.jsonl.
#
# Fixed on the CONSUMPTION side deliberately. The alternative — tightening
# the pass_one prompt so the model phrases topics more consistently — is the
# approach that already failed twice on this codebase (the scope gate's first
# fix, and the pass_three sibling gap; see testing/session_summary_2026-07-30.md
# §9): a prompt guardrail tuned against the variants you have seen generalizes
# to those variants and nothing adjacent. Word-set matching handles every
# reordering of a topic's words at once, including ones never observed, and is
# deterministic and unit-testable without an API call.

# Punctuation that appears in TOPICS entries and in observed model variants;
# normalized to whitespace so it can't affect tokenization. This also turns
# "&" into a separator, which is why it isn't listed as a connective below.
_TOPIC_PUNCTUATION = re.compile(r"[^\w\s]+")

# Connectives carry no topic identity — "Entropy and Exergy", "Entropy &
# Exergy" and "Entropy, Exergy" all name the same topic — so they're dropped
# rather than being allowed to make otherwise-identical labels compare
# unequal. Kept deliberately short: every word removed here is a word that
# can no longer distinguish two topics, and "of" is NOT in the list because
# it does real work in "Laws of Thermodynamics" / "Equations of State".
_TOPIC_CONNECTIVES = frozenset({"and", "or", "vs", "versus"})


def _topic_word_key(topic: str) -> frozenset:
  """Order-independent identity for a topic label: casefolded word set with
  punctuation and connectives stripped. 'Work, Heat, and Energy Transfer' and
  'Heat, Work, and Energy Transfer' both collapse to the same key.

  A set (not a sorted list) is used so duplicate words can't make two
  otherwise-identical labels compare unequal. No TOPICS entry contains a
  repeated word, so nothing is lost by ignoring multiplicity."""
  cleaned = _TOPIC_PUNCTUATION.sub(" ", str(topic))
  return frozenset(cleaned.casefold().split()) - _TOPIC_CONNECTIVES


# Built once at import. Two TOPICS entries colliding on the same word key
# would make canonicalization ambiguous, so that is an assertion, not a
# silent last-one-wins — test_config_consistency.py covers it too.
_TOPIC_BY_WORD_KEY = {}
for _canonical in TOPICS:
  _key = _topic_word_key(_canonical)
  assert _key not in _TOPIC_BY_WORD_KEY, (
    f"TOPICS entries {_TOPIC_BY_WORD_KEY[_key]!r} and {_canonical!r} are "
    f"word-order variants of each other; canonicalization can't disambiguate them."
  )
  _TOPIC_BY_WORD_KEY[_key] = _canonical


def canonicalize_topic(raw_topic):
  """Map a model-generated topic label onto its canonical TOPICS entry.

  Returns the canonical string, or None when there is no confident match.
  None is a real outcome the caller must handle (log it, then fall back) —
  it deliberately does NOT return DEFAULT_REFERENCE's topic or the raw
  label, because 'we could not identify this topic' and 'this topic has no
  reference on file' are different facts and the caller needs to tell them
  apart.

  Matching is exact-after-normalization only: casing, surrounding
  whitespace, punctuation and word order are ignored, nothing else. A label
  that is merely a SUBSET of a topic's words (a bare 'Heat', observed twice
  in the transcript corpus) is NOT matched — 'Heat' is a plausible fragment
  of both 'Heat, Work, and Energy Transfer' and 'Laws of Thermodynamics'-
  adjacent material, and guessing between them would substitute a silent
  wrong-reference bug for the silent missing-reference bug being fixed
  here. Those fall through to None and get logged."""
  if not isinstance(raw_topic, str) or not raw_topic.strip():
    return None
  return _TOPIC_BY_WORD_KEY.get(_topic_word_key(raw_topic))


# --- Deterministic IRL->CONCEPTUAL override -------------------------------
# pass_one's CONCEPTUAL rubric requires the student to be "asking for a
# definition, law, formula, or terminology directly" — a bare "why does X
# hold" / "what is X used for" question with no problem context doesn't
# literally fit that phrasing, so it falls to IRL instead. Tutor's IRL branch
# has no fallback for "no student attempt to scaffold around" (see
# tutor.py), so it produces a bare Socratic question with no real answer.
# This heuristic runs after pass_one and before dispatch (see
# generate_response) to catch that case without touching pass_one's prompt
# or any individual mode handler.
#
# has_problem_context() require either a decimal number, a 2+ digit number
# (word-boundary bounded, so "Q11" inside a question id never matches — see
# _MULTI_DIGIT_NUMBER), a unit/quantity keyword directly adjacent to a
# number, or problem-reference phrasing ("stuck on", "this problem", "how do
# I approach") that signals a specific-but-unquantified problem is in view
# (e.g. "I'm stuck on a Carnot efficiency problem" should stay IRL and get
# Socratic scaffolding, not a bare definition dump).

_DECIMAL_NUMBER = re.compile(r'\b\d+\.\d+\b')
_MULTI_DIGIT_NUMBER = re.compile(r'\b\d{2,}\b')

_UNIT_KEYWORDS = (
  'kpa', 'mpa', 'gpa', 'pa', 'kj', 'mj', 'j', 'kg', 'kmol', 'mol',
  'bar', 'atm', 'kw', 'rpm', 'm3', 'm³', '°c', '°f',
)
_UNIT_NEAR_NUMBER = re.compile(
  r'\b\d+(?:\.\d+)?\s*(?:' + '|'.join(re.escape(u) for u in _UNIT_KEYWORDS) + r')\b',
  re.IGNORECASE,
)
# Short/single-letter units (K, C, F, g, L, W, s, h, min, hr) are only
# treated as unit evidence when a number sits directly next to them, since
# these letters are common enough on their own to false-positive otherwise.
_SHORT_UNIT_NEAR_NUMBER = re.compile(
  r'\b\d+(?:\.\d+)?\s*(?:k|c|f|g|l|w|s|h|min|hr)\b',
  re.IGNORECASE,
)

_PROBLEM_REFERENCE_PHRASES = (
  'stuck on', 'stuck with', "don't know where to start", "do not know where to start",
  'where to start', 'how do i approach', 'how do i start', 'how do i even',
  "i've never done", "i have never done", 'help me start',
  'my problem', 'this problem', 'the problem', 'a problem where', 'a problem in which',
  'given that', 'given the following', 'given:',
)


def has_problem_context(conversation_history: list, current_message: str) -> bool:
  """True if the current message or the same rolling window pass_one saw
  contains evidence of an actual problem in view (numeric values, units, or
  given-quantity/problem-reference phrasing) rather than a bare factual ask."""
  recent = conversation_history[-PASS_ONE_HISTORY_WINDOW:]
  scope_text = " ".join(turn["content"] for turn in recent) + " " + current_message
  scope_lower = scope_text.lower()

  if _DECIMAL_NUMBER.search(scope_text):
    return True
  if _MULTI_DIGIT_NUMBER.search(scope_text):
    return True
  if _UNIT_NEAR_NUMBER.search(scope_text):
    return True
  if _SHORT_UNIT_NEAR_NUMBER.search(scope_text):
    return True
  if any(phrase in scope_lower for phrase in _PROBLEM_REFERENCE_PHRASES):
    return True
  return False


def _format_history_for_pass_one(conversation_history: list) -> str:
  recent = conversation_history[-CONVERSATION_HISTORY_WINDOW:]
  if not recent:
    return "(no prior turns in this conversation)"
  return "\n".join(
    f"{'Student' if turn['role'] == 'user' else 'Tutor'}: {turn['content']}"
    for turn in recent
  )


PASS_ONE_HISTORY_WINDOW = CONVERSATION_HISTORY_WINDOW  # window has_problem_context() scans; shares pass_one's history window
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


_NULLISH_PROPOSED_VALUES = {"", "null", "none", "n/a", "na", "nan", "unknown"}


def _clean_proposed_value(raw) -> str:
  """Normalize pass_one's proposed_value into a usable claim string, or None.

  Accepts a number as well as a string, since the model sometimes emits a bare
  JSON number for a numeric claim. Returns None for anything unusable — missing,
  JSON null, empty, or a string spelling of null the model produced instead of a
  real one — so the caller can fail safe rather than verify against a non-claim."""
  if isinstance(raw, bool) or raw is None:
    return None
  if isinstance(raw, (int, float)):
    return str(raw)
  if not isinstance(raw, str):
    return None
  cleaned = raw.strip()
  if not cleaned or cleaned.lower() in _NULLISH_PROPOSED_VALUES:
    return None
  return cleaned


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
      "has_proposed_answer": true or false,
      "proposed_value": "the student's own claimed answer exactly as they stated it, or null",
      "reasoning_gap": "brief description of what the student is missing/asking",
      "misconception": "specific misconception if one exists, otherwise null"
    }}

    Classification rules:
    - IPS: student has encountered this concept before but is making an execution error
    - IRL: concept is new to the student
    - CONCEPTUAL: student is asking for a definition, law, formula, or terminology directly, with no problem context, numeric values, or reference to their own attempt
    - CONFIRMATION: the student has already worked through a specific problem (in this message or earlier in the conversation history) and has a specific result on the table, and is now asking for a verdict on it — e.g. "so delta U = 300 J, right?", "I got Wb = 45 kJ, is that correct?", "I think it should be negative — am I right?". Note that the verdict-seeking phrasing alone is never what makes it CONFIRMATION: a bare "is that correct?" or "can you just tell me if I'm right or wrong?" qualifies ONLY when the student's own specific result is actually in view (in this message or earlier in the conversation history). Use the conversation history to check whether a derivation/result was already stated before classifying this way; a bare "is that right?" with no prior derivation in view is not enough on its own.

    has_proposed_answer rules (judge this INDEPENDENTLY of the classification above):
    - true ONLY if the student has committed to a specific answer of their own — either a specific value ("I got 45 kJ", "so delta U = 300 J") or a specific directional/qualitative conclusion ("I think it should be positive", "I believe the entropy decreases", "it must be zero") — stated as their OWN claim, in this message or earlier in the conversation history.
    - false for open questions ("is the change in internal energy positive or negative?"), requests for the answer ("just give me the final number", "finish the derivation for me"), and demands for a verdict with no claim of their own attached ("yes or no?", "just yes or no", "come on, yes or no?", "is it positive?").
    - Repetition, insistence, or frustration NEVER makes this true. A student demanding a verdict for the fourth time still has no proposed answer unless they have actually stated one. Asking "is it positive?" is a question, not a claim; saying "I think it's positive" is a claim.
    - Claimed competence is not a proposed answer: "I've got (a) and (b) worked out" or "I've shown I understand the method" asserts understanding, not a specific result, so it stays false unless the actual result is stated.
    - A symbolic or algebraic setup the student has NOT evaluated is not a proposed answer. "I set up q - w = delta h, so w = h1 - h2, can you finish it?" states a relationship they have not yet computed — that is false, not true. If producing a value would require YOU to do the arithmetic for them, they have not proposed an answer.

    proposed_value rules:
    - Decide has_proposed_answer FIRST, on its own rules above. Only if it is true do you fill this in. Finding a candidate value here is never a reason to flip has_proposed_answer to true.
    - If has_proposed_answer is false, set this to null.
    - A word or number that appears only inside the student's QUESTION is not their claim. In "Yes or no -- is it positive?" the student is asking whether it is positive, not asserting that it is: has_proposed_answer is false and this is null. Extract only what the student asserts, never what they are asking about.
    - Otherwise extract ONLY the answer the student is claiming as their OWN result, in their own words and units exactly as written — e.g. "215.4 kJ", "+65 kJ", "-94.6 kJ".
    - NEVER extract a value the problem gave them, a physical constant, or an intermediate quantity from their formula or working. In "I calculated Q = 215.4 kJ using Q = m·cv·ΔT with cv = 0.718 kJ/kg·K", the proposed_value is "215.4 kJ" — NOT 0.718 (a constant they were using) and NOT any given temperature or mass. The student's claim is not identified by where it appears in the sentence: it may come before or after their supporting work, so read for meaning rather than taking the first or last number.
    - For a directional or qualitative claim with no number, capture the claim as stated — e.g. "positive", "negative", "zero", "it increases" — not a number.
    - Copy what the student actually wrote. NEVER compute, evaluate, simplify, rearrange, or infer a value they did not write down themselves. Given "w = -delta h = h1 - h2" with h1 and h2 supplied earlier, you must NOT return "350 kJ" or "-350 kJ" — the student never wrote that number, so has_proposed_answer is false and this is null. If you cannot quote the value from their own words, there isn't one.
    - Report the value alone, without the surrounding sentence and without any of your own commentary.


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

  turn_usage.record("gpt-4o-mini", pass_one_analysis.usage.prompt_tokens, pass_one_analysis.usage.completion_tokens)

  diagnosis = json.loads(pass_one_analysis.choices[0].message.content)
  raw_topic = diagnosis.pop("topic")

  # Canonicalized here, at the single point where the raw label leaves
  # pass_one, rather than at the generate_response() call site — this way no
  # consumer can ever observe the raw form, whether it's get_reference(),
  # the pass_two prompt, or the transcript the harnesses log. See
  # canonicalize_topic() above for why this is a consumption-side fix.
  topic = canonicalize_topic(raw_topic)
  if topic is None:
    # Unrecognized even after normalization. The student-visible behavior is
    # unchanged (get_reference falls back to DEFAULT_REFERENCE exactly as
    # before), but this used to be completely invisible — the whole point of
    # the warning is that the next occurrence is traceable instead of silent.
    logger.warning(
      "pass_one returned an unrecognized topic label %r (not a word-order "
      "variant of any TOPICS entry); falling back to DEFAULT_REFERENCE. "
      "Student input began: %r",
      raw_topic,
      user_input[:120],
    )
    topic = raw_topic

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
  turn_usage.reset()

  # Scope gate runs before Pass 1 classification, on every turn (not just the
  # opening one) — a topic that's out of bounds shouldn't be answered whether
  # it lands on IPS, IRL, CONCEPTUAL, or CONFIRMATION, so this sits upstream
  # of that routing entirely rather than being patched into one branch. The
  # redirect itself is a fixed string, not model generation — see
  # scope_check.REDIRECT_MESSAGE.
  if not check_scope(user_input, conversation_history):
    diagnostics = {
      "classification": "OUT_OF_SCOPE",
      "reasoning_gap": None,
      "misconception": None,
      "total_tokens": turn_usage.total_tokens,
      "total_cost_usd": turn_usage.total_cost_usd,
    }
    return REDIRECT_MESSAGE, "Out of Scope", diagnostics

  topic, diagnosis = pass_one(user_input, conversation_history)
  diagnosis_dict = json.loads(diagnosis)
  classification = diagnosis_dict.get("classification")

  # Deterministic override, scoped to IRL only (IPS/CONFIRMATION already
  # require an existing attempt/result in view per their own pass_one rules,
  # so they're left untouched). See has_problem_context() above for why.
  if classification == "IRL" and not has_problem_context(conversation_history, user_input):
    classification = "CONCEPTUAL"
    diagnosis_dict["classification"] = classification
    diagnosis = json.dumps(diagnosis_dict)

  # Verification runs only when the student has actually committed to an answer
  # of their own — there must be something of theirs TO check. This replaced an
  # earlier `classification == "CONFIRMATION" or contains_stated_answer(...)`
  # OR-gate, under which a bare demand for a verdict ("just yes or no") was
  # routinely classified CONFIRMATION, sent to verify_answer() with the demand
  # itself standing in as the "student answer" (see _extract_verification_inputs,
  # which unconditionally uses user_input), and came back with a CORRECT/INCORRECT
  # verdict on a non-answer — which then satisfied tutor.py's direct-verdict
  # branch and leaked the result. pass_one's own has_proposed_answer judgment is
  # primary because it can see conversation history; contains_proposed_answer is
  # the deterministic fallback for a missing/malformed field only. Deliberately
  # does not pass conversation_history into verify_answer itself — see
  # _extract_verification_inputs.
  raw_flag = diagnosis_dict.get("has_proposed_answer")
  has_proposed_answer = raw_flag if isinstance(raw_flag, bool) else contains_proposed_answer(user_input)
  # Normalize back onto the diagnosis so downstream mode handlers read a real
  # bool rather than re-deriving it or tripping over a missing key.
  diagnosis_dict["has_proposed_answer"] = has_proposed_answer
  proposed_value = _clean_proposed_value(diagnosis_dict.get("proposed_value"))
  diagnosis_dict["proposed_value"] = proposed_value
  diagnosis = json.dumps(diagnosis_dict)

  # WHAT the student claimed comes from pass_one's proposed_value, not from a
  # regex over the raw message — see verification._last_stated_number for the
  # failure mode that approach had. If pass_one says there's a proposed answer
  # but didn't give a usable value for it, fail safe: skip verification rather
  # than guessing at the claim from raw text, which is exactly the bug being
  # fixed. verification stays None, so tutor.py's direct-verdict branch can't
  # fire and the turn routes to the Socratic branch.
  verification = None
  if has_proposed_answer and proposed_value:
    problem_statement, student_answer = _extract_verification_inputs(user_input, conversation_history)
    verification = verify_answer(problem_statement, student_answer, topic, proposed_value)

  system_response, gave_direct_answer = pass_two(user_input, diagnosis, topic, conversation_history, mode, verification)

  if not gave_direct_answer and contains_phrase(system_response):
    system_response = pass_three(system_response, topic)

  diagnostics = json.loads(diagnosis)
  if verification:
    diagnostics["verification_verdict"] = verification.get("verdict")
    diagnostics["verification_tier"] = verification.get("tier")

  diagnostics["total_tokens"] = turn_usage.total_tokens
  diagnostics["total_cost_usd"] = turn_usage.total_cost_usd

  return system_response, topic, diagnostics
