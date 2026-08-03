import os
import re
import ast
import json
import operator
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from architecture.config.topic_reference import get_reference
from architecture.testing.cost_tracker import turn_usage

dotenv_path = Path(__file__).parents[2] / ".env"
load_dotenv(dotenv_path)

API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)

VALID_VERDICTS = ("CORRECT", "INCORRECT", "UNCERTAIN")

_CONFIRMATION_PHRASES = (
    "is that right", "is that correct", "final answer", "right or wrong",
    "correct?", "confirm", "am i right", "am i correct",
)


def contains_stated_answer(text: str) -> bool:
    """Lightweight, independent backstop for detecting 'student has stated a
    specific answer and wants a verdict on it' — does not depend on pass_one's
    CONFIRMATION classification, so it can catch cases classification misses.
    Intentionally requires both a number AND confirmation-seeking language, to
    avoid firing on every message that merely contains a digit."""
    has_digit = any(c.isdigit() for c in text)
    has_confirmation_language = any(p in text.lower() for p in _CONFIRMATION_PHRASES)
    return has_digit and has_confirmation_language


# A student can commit to an answer without ever writing a number — "I think it
# should be positive" is as much a claim as "I got 45 kJ", and the tutor owes it
# the same verdict. _CLAIM_OPENERS are first-person commitment markers; a
# directional claim only counts when an opener is followed by a direction word,
# so an open question ("is it positive or negative?") — which carries the
# direction word but no commitment — stays false. This is deliberately narrow:
# it is the deterministic FALLBACK for when pass_one omits has_proposed_answer,
# not the primary gate, so a miss degrades to Socratic (safe) rather than to an
# unearned direct verdict.
_CLAIM_OPENERS = (
    "i think", "i believe", "i got", "i calculated", "i found", "i'd say",
    "i would say", "my answer", "my guess", "it should be", "it must be",
    "it has to be", "i'm saying", "im saying", "i say", "so it's", "so its",
    "pretty sure", "i reckon", "i'm guessing", "im guessing",
)

_DIRECTION_WORDS = (
    "positive", "negative", "zero", "increase", "increases", "increasing",
    "decrease", "decreases", "decreasing", "rises", "rising", "falls",
    "falling", "constant", "unchanged", "greater", "larger", "smaller",
    "less", "higher", "lower", "same",
)


def contains_directional_claim(text: str) -> bool:
    """True when the student commits to a qualitative/directional conclusion of
    their own (no number required) — e.g. 'I think it should be positive'.
    Requires a first-person commitment opener followed (within the same message)
    by a direction word, so bare questions and repeated demands for a verdict
    ('is it positive?', 'yes or no?') do NOT qualify."""
    lowered = text.lower()
    for opener in _CLAIM_OPENERS:
        idx = lowered.find(opener)
        while idx != -1:
            tail = lowered[idx + len(opener):]
            if any(word in tail for word in _DIRECTION_WORDS):
                return True
            idx = lowered.find(opener, idx + 1)
    return False


def contains_proposed_answer(text: str) -> bool:
    """Deterministic fallback for 'has the student committed to an answer of
    their own?' — numeric claim (contains_stated_answer) OR directional claim
    (contains_directional_claim). Used only when pass_one's has_proposed_answer
    field is missing or malformed; pass_one's own judgment is the primary
    signal because it can see the conversation history, which this cannot."""
    return contains_stated_answer(text) or contains_directional_claim(text)


# deterministic arithmetic check
_ALLOWED_BINOPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
}
_ALLOWED_UNARYOPS = {
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
}

_PURE_ARITHMETIC = re.compile(r'^[\d,\.\+\-\*/\(\)\s]+$')
_LEADING_NUMBER = re.compile(r'^\s*(-?[\d,]+\.?\d*)')


def _safe_eval(expr: str):
    node = ast.parse(expr, mode="eval").body
    return _eval_node(node)


def _eval_node(node):
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_BINOPS:
        return _ALLOWED_BINOPS[type(node.op)](_eval_node(node.left), _eval_node(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_UNARYOPS:
        return _ALLOWED_UNARYOPS[type(node.op)](_eval_node(node.operand))
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    raise ValueError(f"unsupported expression node: {node}")


def _check_arithmetic(text: str) -> dict:
    """Find self-contained 'expression = number' equations in text (e.g. from
    a student showing their work) and re-evaluate them in code. Splits on '='
    and checks every ADJACENT pair of segments independently (rather than a
    single regex scan) so that filtering out a junk pair — e.g. a bare
    variable name like 'Q =' — can't cause the next pair's match to skip past
    digits that belong to it. Only flags equations where the left-hand side is
    pure arithmetic (digits/operators/parens only, no embedded units/letters)
    — plain assignments like 'Q = -50 kJ' or unit-embedded expressions like
    '-50 kJ - (500 kJ)' are left alone since they can't be safely evaluated in
    code; those fall through to the semantic tier instead. Treated as ground
    truth when it finds a mismatch."""
    segments = text.split("=")
    checks = []
    for i in range(len(segments) - 1):
        lhs = segments[i].strip()
        if not lhs or not _PURE_ARITHMETIC.match(lhs):
            continue
        if not any(op in lhs for op in "+-*/") or not any(c.isdigit() for c in lhs):
            continue
        rhs_match = _LEADING_NUMBER.match(segments[i + 1])
        if not rhs_match:
            continue
        try:
            lhs_value = _safe_eval(lhs.replace(",", ""))
            rhs_value = float(rhs_match.group(1).replace(",", ""))
        except (ValueError, SyntaxError, TypeError, ZeroDivisionError):
            continue
        tolerance = max(abs(rhs_value) * 0.01, 0.5)
        matches = abs(lhs_value - rhs_value) <= tolerance
        checks.append({
            "expression": lhs, "computed": lhs_value, "stated": rhs_value, "matches": matches,
        })

    if not checks:
        return {"tier_result": "NO_EQUATION_FOUND", "checks": []}

    failing = [c for c in checks if not c["matches"]]
    if failing:
        return {"tier_result": "ARITHMETIC_ERROR", "checks": checks, "failing": failing}
    return {"tier_result": "ARITHMETIC_OK", "checks": checks}


# semantic / convention check
def _extract_number(text) -> float:
    """Pull the first numeric value out of a short string like '450 kJ' or
    '-550 kJ'. Returns None if nothing parseable is found."""
    if text is None:
        return None
    match = re.search(r'-?[\d,]+\.?\d*', str(text))
    if not match:
        return None
    try:
        return float(match.group(0).replace(",", ""))
    except ValueError:
        return None


def _semantic_check(problem_statement: str, student_answer: str, topic: str, proposed_value: str) -> dict:
    reference = get_reference(topic)

    # Explicitly scaffolds "who is the system / which direction is work or heat
    # crossing the boundary" as separate reasoning steps before the model commits
    # to signs. Testing found the model would otherwise inconsistently flip the
    # sign of W on "external agent does work ON the system" phrasings (e.g. "a
    # pump does work on a fluid") even when given the correct reference formula —
    # forcing the direction identification as its own field measurably reduced
    # (but did not eliminate) that error.
    prompt = f"""
    You are independently verifying a thermodynamics student's answer against known
    reference conventions. You are a checker, not a tutor — do not hedge, do not be
    encouraging, just work the problem and compare.

    Reference formulas/conventions for this topic:
    {reference}

    Problem statement (as stated by the student; may be partial or come from earlier
    in the conversation):
    {problem_statement}

    Student's stated derivation/answer to check:
    {student_answer}

    The specific result the student is claiming as their own answer (already
    identified for you — compare against THIS, not against any given value,
    constant, or intermediate quantity appearing in their working):
    {proposed_value}

    Before applying any signs, first explicitly identify:
    1. What is "the system" in this problem?
    2. For any work term: is work being done BY the system on the surroundings, or ON
       the system by the surroundings/an external agent (e.g. a pump or compressor
       acting on a fluid does work ON the fluid — if the fluid is the system, that is
       work done ON the system)?
    3. For any heat term: is heat entering or leaving the system?

    Then apply the sign convention from the reference material and compute the result
    yourself, independent of the student's setup — do not assume their signs are right.

    Respond with this exact JSON format:
    {{
      "system_identification": "what/who is the system",
      "work_direction": "ON the system or BY the system, and why",
      "heat_direction": "entering or leaving the system, and why",
      "step_by_step_reasoning": "your own independent derivation, a few sentences",
      "correct_value": "the value/result your own derivation arrives at",
      "verdict": "CORRECT if the student's answer matches your derivation, INCORRECT if it doesn't, or UNCERTAIN if the problem statement is too incomplete to independently verify"
    }}
    """

    completion = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.2,
        response_format={"type": "json_object"},
    )
    turn_usage.record("gpt-4o", completion.usage.prompt_tokens, completion.usage.completion_tokens)

    result = json.loads(completion.choices[0].message.content)

    # The model's own "verdict" field has been observed to disagree with its own
    # "correct_value" (e.g. computing 450 kJ but still labeling the student's
    # 450 kJ answer INCORRECT). Where both correct_value and the student's own
    # stated final number can be parsed, derive the verdict by comparing them in
    # code instead of trusting the model's self-reported verdict outright.
    #
    # student_value comes from pass_one's extracted proposed_value, NOT from a
    # regex over the raw message. The previous approach (_last_stated_number,
    # "the number after the last '='") had no way to tell a claimed answer from a
    # constant: on "Q = 215.4 kJ using Q = m·cv·ΔT with cv = 0.718 kJ/kg·K" it
    # picked up 0.718, and this comparison then manufactured an INCORRECT verdict
    # against a model derivation that had actually agreed with the student.
    # Position in the sentence is simply not a signal for which number is the
    # student's claim, in either order, so identifying it is left to the pass_one
    # call that already reads the message for meaning. The comparison itself is
    # unchanged and still fully deterministic. A qualitative claim ("positive")
    # parses to None here and correctly defers to the semantic verdict below.
    model_value = _extract_number(result.get("correct_value"))
    student_value = _extract_number(proposed_value)
    if model_value is not None and student_value is not None:
        tolerance = max(abs(model_value) * 0.01, 0.5)
        result["verdict"] = "CORRECT" if abs(model_value - student_value) <= tolerance else "INCORRECT"
    elif result.get("verdict") not in VALID_VERDICTS:
        result["verdict"] = "UNCERTAIN"

    return result


def _last_stated_number(text: str):
    """RETIRED as a source of truth — no longer called by verify_answer().

    Best-effort extraction of the student's final stated numeric answer: the
    number immediately after the last '=' sign, if there is one, else the last
    number anywhere in the text. This is unreliable by construction — sentence
    position does not distinguish a claimed answer from a constant or a given
    value ("Q = 215.4 kJ ... with cv = 0.718" yields 0.718), and the fallback
    branch additionally matches bare commas and mis-handles a leading '+'.
    pass_one's proposed_value field replaced it; see _semantic_check. Kept only
    so the failure mode stays documented in one place — do not reintroduce it
    into the verification path."""
    segments = text.split("=")
    if len(segments) > 1:
        match = _LEADING_NUMBER.match(segments[-1])
        if match:
            return match.group(1)
    all_numbers = re.findall(r'-?[\d,]+\.?\d*', text)
    return all_numbers[-1] if all_numbers else None


# combined verdict
def verify_answer(problem_statement: str, student_answer: str, topic: str, proposed_value: str) -> dict:
    """Check a student's stated answer against static reference material —
    deliberately does NOT take conversation_history, so it can't inherit
    drift from the tutor's own earlier (possibly wrong) turns in this
    conversation. Callers are responsible for sourcing problem_statement /
    student_answer from raw student-authored text only.

    proposed_value is the student's own claimed answer as identified by
    pass_one ("215.4 kJ", "positive"), and is what the deterministic
    correctness comparison is made against. Callers must not synthesize it by
    regex over the raw message — that is the bug this parameter exists to fix
    — and should skip verification entirely when pass_one didn't produce one.

    Returns: {"verdict": CORRECT|INCORRECT|UNCERTAIN, "tier": deterministic|semantic|disagreement,
              "correct_value": ..., "reasoning": ...}
    """
    arithmetic = _check_arithmetic(student_answer)
    semantic = _semantic_check(problem_statement, student_answer, topic, proposed_value)

    if arithmetic["tier_result"] == "ARITHMETIC_ERROR":
        if semantic.get("verdict") == "CORRECT":
            # Tiers disagree: the arithmetic as literally written doesn't check
            # out, but the semantic pass thinks the student is right anyway.
            # Don't trust either one blindly — fall back to uncertain.
            return {
                "verdict": "UNCERTAIN",
                "tier": "disagreement",
                "correct_value": semantic.get("correct_value"),
                "reasoning": (
                    f"Deterministic check found an arithmetic inconsistency "
                    f"({arithmetic['failing']}), but the semantic check says CORRECT. "
                    f"Flagging as uncertain rather than trusting either tier."
                ),
            }
        return {
            "verdict": "INCORRECT",
            "tier": "deterministic",
            "correct_value": semantic.get("correct_value"),
            "reasoning": f"Arithmetic error found in the student's own equation(s): {arithmetic['failing']}",
        }

    # No arithmetic error found (or nothing checkable) — arithmetic tier is
    # inconclusive on its own, defer entirely to the semantic tier.
    return {
        "verdict": semantic.get("verdict", "UNCERTAIN"),
        "tier": "semantic",
        "correct_value": semantic.get("correct_value"),
        "reasoning": semantic.get("step_by_step_reasoning"),
    }
