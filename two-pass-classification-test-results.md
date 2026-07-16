# 20-Prompt Test of the Two-Pass Classifier & Scaffold

## What was tested

20 prompts were run through the live `pass_one` → `pass_two` pipeline in `two_pass_engine.py` (post-fix, see `scaffolding-over-conceptual-questions.md`): 10 written to be unambiguous `CONCEPTUAL` asks, and 10 written to be `IPS`/`IRL` (execution error / new-concept) asks — including a couple of deliberately awkward edge cases in each group to probe robustness rather than just confirm the easy cases. All ran with empty conversation history, `gpt-4o-mini`, same temperatures as production (0.1 for pass one, 0.7 for pass two).

## Results at a glance

| # | Input (truncated) | Classification | Correct? |
|---|---|---|---|
| C1 | What is the second law of thermodynamics? | CONCEPTUAL | ✅ |
| C2 | Define specific heat capacity. | CONCEPTUAL | ✅ |
| C3 | What is an isothermal process? | CONCEPTUAL | ✅ |
| C4 | What's the ideal gas law equation? | CONCEPTUAL | ✅ |
| C5 | Difference between enthalpy and internal energy? | CONCEPTUAL | ✅ |
| C6 | What does it mean for a process to be adiabatic? | CONCEPTUAL | ✅ |
| C7 | Clausius statement of the second law? | CONCEPTUAL | ✅ |
| C8 | Can you explain what exergy is? | CONCEPTUAL | ✅ |
| C9 | What is the triple point of water? | CONCEPTUAL | ✅ |
| C10 | Why does entropy always increase in an isolated system? (edge: "why" phrasing) | CONCEPTUAL | ✅ |
| I1 | Piston-cylinder work sign error (-500 J) | IPS | ✅ |
| I2 | Refrigeration COP calculated as 0.5, expected >1 | IPS | ✅ |
| I3 | Carnot efficiency calculated as 1.6 | IPS | ✅ |
| I4 | Ideal gas law off by 100x, guesses Celsius/Kelvin mixup | IPS | ✅ |
| I5 | First time reading a psychrometric chart | IRL | ✅ |
| I6 | Never calculated exergy destruction before | IRL | ✅ |
| I7 | Rankine cycle, negative pump work | IPS | ⚠️ (see below) |
| I8 | Negative entropy generation in a closed system | IPS | ✅ |
| I9 | First open-system energy balance, mass flow rates given | IRL | ✅ |
| I10 | "What is exergy, and how do I calculate it for my system with T0=298K, P1=200kPa?" (edge: mixed intent) | IRL | ✅ |

**20/20 classified into the intended top-level bucket** (`CONCEPTUAL` vs. `IPS`/`IRL`). All 10 `CONCEPTUAL` responses answered directly with no trailing question — the fix holds under a broader prompt set, not just the 3-4 prompts it was originally tuned against.

## Strengths

**1. The CONCEPTUAL fix generalizes.** Every one of the 10 conceptual prompts — spanning laws, definitions, formulas, and one "why" phrasing (C10) that could plausibly have been read as an explanation request needing scaffolding — got a direct, correct, complete answer ending in an inviting statement, never a question. This wasn't cherry-picked; C10 in particular was included specifically to see if "why" framing would trip the classifier back into scaffold mode, and it didn't.

**2. The classifier resists the obvious adversarial case.** I10 was designed to break it: it opens with the exact "What is X" pattern that defines `CONCEPTUAL`, but appends real problem context (T0, P1 values, "my system"). It was correctly routed to `IRL`, not `CONCEPTUAL` — the numeric, own-system context outweighed the surface phrasing. Worth noting: the response to I10 happened to answer the "what is exergy" half plainly before scaffolding the calculation half, which is exactly the ideal behavior for a mixed prompt — but see Weakness 4, this wasn't a designed behavior.

**3. No answer leakage observed in the IPS/IRL set.** None of the 10 scaffolded responses stated the final correct value or explicitly confirmed/denied the student's hypothesis. Even where a student essentially named the bug themselves (I3: "efficiency can't be right", I4: "is that the problem?"), the tutor didn't just say "yes."

**4. IPS vs. IRL sub-classification is internally consistent.** Prompts describing a specific calculation gone wrong were reliably tagged `IPS` (I1-I4, I7-I8); prompts describing unfamiliarity with a new tool/concept were reliably tagged `IRL` (I5, I6, I9, I10). Pass one is tracking a real distinction here — it's just not being used downstream (see Weakness 3).

## Weaknesses

**1. No "confirm and reinforce" path when a student self-diagnoses correctly (I4).** The student explicitly guessed the right root cause: *"I used Celsius instead of Kelvin, is that the problem?"* The response didn't engage with that guess at all — it pivoted to a generic "why is Kelvin important?" question, ignoring that the student had already done the reasoning. Repeated over a real session, this reads as evasive rather than responsive. The architecture has no signal for "the student already found it, just confirm."

**2. The line between "reminding a formula" and "revealing the answer" is fuzzier in the IPS branch than in the new CONCEPTUAL branch (I3).** For the Carnot-efficiency-of-1.6 case, the response restated the full Carnot efficiency formula before asking for the student's inputs. That's defensible pedagogically (the formula isn't the specific error), but the IPS/IRL prompt still just says "do not reveal the diagnosis or the correct answer" with no guidance on what counts as an acceptable formula reminder — it's exactly the ambiguity the CONCEPTUAL fix eliminated for direct asks, but it still exists here.

**3. IPS and IRL get an identical prompt in `pass_two`, despite `pass_one` reliably telling them apart.** A brand-new-to-the-student concept (IRL) plausibly needs a sentence of grounding before the Socratic question; an execution error on a familiar concept (IPS) can jump straight to the diagnostic question. Right now that distinction is computed and then thrown away.

**4. Good handling of mixed conceptual+application prompts (I10) looks like luck, not design.** Nothing in the `IPS`/`IRL` prompt tells the model "if part of this question is a bare definitional ask, answer that part directly." It happened to do the right thing at temperature 0.7 this run; there's no guarantee across runs, and a regression here would look identical to the original bug this session's fix targeted, just scoped to mixed prompts instead of pure ones.

**5. Unrelated but worth flagging: possible content error in I7.** Pass one flagged "negative pump work" as a misconception, but negative pump work is the expected sign under a "work done by the system" convention (a pump does work *on* the fluid). If this is in fact a misdiagnosis, `pass_two` would be scaffolding the student toward a wrong idea. This is a domain-accuracy issue in pass one's reasoning, not a scaffolding-architecture issue, but it's the kind of thing that's invisible unless someone reads the actual diagnosis JSON, since it's never shown to the student.

**6. Conversation history was untested.** All 20 runs used an empty history. The system prompt claims the tutor uses "prior concept history ... to calibrate scaffold depth," but that behavior has zero test coverage here — multi-turn dynamics (e.g., not re-asking a question the student already answered) are unverified.

## Where to improve from here

1. **Split `IPS` vs. `IRL` behavior in `pass_two`.** Since pass one already separates them reliably (confirmed across 6 IPS and 4 IRL cases here), give IRL a short grounding sentence before the diagnostic question, and let IPS go straight to the diagnostic question.
2. **Add a "student self-diagnosed correctly" signal.** Have pass one flag when the student's own message already contains a plausible correct hypothesis (could be a new boolean field), and let pass two affirm it directly instead of always defaulting to an open question — this directly addresses Weakness 1 (I4).
3. **Tighten the IPS/IRL "don't reveal the answer" instruction** the same way the CONCEPTUAL branch was tightened: give an explicit example of what's fine to restate (a general formula) vs. what isn't (the specific corrected value or which of the student's numbers is wrong).
4. **Consider a fourth classification, or a boolean flag, for mixed conceptual+application prompts** so the "answer the definitional part directly, scaffold the rest" behavior seen in I10 is a designed instruction rather than an artifact of sampling temperature.
5. **Spot-check pass one's `misconception` field against a domain reference** for a batch of IPS/IRL cases (starting with I7) — an incorrect misconception fed into pass two is a silent failure mode, since the diagnosis is never shown to the student and therefore never self-corrects.
6. **Run a multi-turn version of this test** — same 10 IPS/IRL prompts, but with 2-3 turns of prior conversation history — to actually exercise the "calibrate scaffold depth" claim in the system prompt instead of assuming it works.
