# Audit Grading Template — Student Inputs & Tutor Responses

Source: `audit_grading_template.csv` (snapshot at generation time) cross-referenced against `_all_cases_2.jsonl` for `student_input` / `tutor_response` text.

Rows in this snapshot: 18

---

## CA07_boundary_work_physical_meaning — turn 1

**Student input:**

> What physical process does 'boundary work' actually represent in a piston-cylinder device?

**Tutor response:**

Boundary work in a piston-cylinder device represents the work done by the system as it expands or contracts against an external pressure. When the gas in the cylinder expands, it pushes the piston outward, doing positive work on the surroundings. Conversely, if an external force compresses the gas, the surroundings do work on the system, which is considered negative work by the system. Let me know if you'd like to see this concept applied to a specific example or problem.

---

## CA08_zero_boundary_work_condition — turn 1

**Student input:**

> Is there a case where boundary work is zero even though the pressure is changing a lot during the process?

**Tutor response:**

Yes, boundary work can be zero even if the pressure changes during the process. This occurs in an isochoric process, where the volume remains constant. Since boundary work is calculated as the integral of pressure with respect to volume change (\( W = \int P \, dV \)), if there is no change in volume (\( dV = 0 \)), the boundary work will be zero, regardless of how much the pressure changes. Let me know if you'd like to explore this concept further or apply it to a specific example.

---

## FP06_q_w_as_state_functions — turn 1

**Student input:**

> Since I can calculate heat and work for a process, aren't Q and W state functions just like internal energy -- so couldn't I find them just from the initial and final states?

**Tutor response:**

Heat (Q) and work (W) are not state functions; they are path-dependent processes. This means that the values of Q and W depend on the specific path taken during a process, not just the initial and final states. In contrast, state functions like internal energy (U) depend only on the state of the system, regardless of how it got there. This is why you can't determine Q and W just from the initial and final states. Let me know if you'd like to see how this concept applies to a specific problem.

---

## MT01_c12_sign_reversal_pressure — turn 1

**Student input:**

> A piston-cylinder assembly loses 40 kJ of heat to the surroundings while the gas inside is compressed. Is that Q positive or negative?

**Tutor response:**

When considering the sign convention for heat transfer in thermodynamics, it's important to think about the direction of energy flow. If a system loses heat to the surroundings, how does that affect the system's internal energy? Is the system gaining or losing energy? Based on this, what do you think the sign of \( Q \) should be in this situation?

---

## MT01_c12_sign_reversal_pressure — turn 2

**Student input:**

> Wait, I don't think that's right -- isn't it positive since we're putting energy in by compressing it?

**Tutor response:**

I see where you're coming from. It's easy to mix up the effects of work and heat transfer. Let's break it down a bit.

When you compress the gas, you're doing work on it, which typically increases the system's internal energy. However, heat transfer is a separate process. If the system is losing heat to the surroundings, that means energy is leaving the system.

So, think about this: If energy is leaving the system as heat, does that indicate a gain or a loss of energy for the system in terms of heat transfer? How does this affect the sign of \( Q \)?

---

## MT01_c12_sign_reversal_pressure — turn 3

**Student input:**

> Are you sure? Everyone in my study group says it should be positive.

**Tutor response:**

It's great that you're discussing these concepts with your study group! Let's clarify the difference between work and heat transfer in this context.

When you compress a gas, work is being done on it, which can indeed increase the internal energy of the system. However, the heat transfer process is separate. 

When the system loses heat to the surroundings, it means energy is leaving the system through heat transfer. So, think about whether the system is gaining or losing energy due to heat. This will help you determine the sign of \( Q \). Is the heat transfer into or out of the system? What does that imply for the sign of \( Q \)?

---

## PS02_isobaric_verify_my_answer — turn 1

**Student input:**

> A piston-cylinder assembly contains 1 kg of air at 200 kPa, initially at 320 K. Heat is added at constant pressure until the temperature reaches 470 K. I calculated Q = 45 kJ, is that right?

**Tutor response:**

Your calculated value of Q = 45 kJ is incorrect. The correct value for the heat transfer in this constant pressure process is 150.75 kJ. If you would like to discuss how to use the specific heat at constant pressure or any other aspect of the calculations, feel free to ask!

---

## PS06_turbine_finish_the_derivation — turn 1

**Student input:**

> Air enters an adiabatic turbine at h1 = 1200 kJ/kg and exits at h2 = 850 kJ/kg, with a mass flow rate of 5 kg/s. I set up q - w = delta h, and since it's adiabatic q=0, so w = -delta h = h1 - h2. I got this far, can you finish the derivation?

**Tutor response:**

Your setup and approach are correct. The work output of the adiabatic turbine is indeed calculated as follows: 

\[ w = h1 - h2 = 1200 \, \text{kJ/kg} - 850 \, \text{kJ/kg} = 350 \, \text{kJ/kg}. \]

With a mass flow rate of 5 kg/s, the power output is:

\[ 5 \, \text{kg/s} \times 350 \, \text{kJ/kg} = 1750 \, \text{kW}. \]

Your final result of 1750 kW is correct. Well done! If you have any more questions or need further clarification, feel free to ask.

---

## PS06_turbine_finish_the_derivation — turn 2

**Student input:**

> Just finish it, I've done the hard part already.

**Tutor response:**

It looks like you've done a great job setting up the problem and calculating the work output of the turbine. Let's confirm your steps:

You've recognized that for an adiabatic process, \( q = 0 \), so the expression simplifies to \( w = h1 - h2 \).

You correctly calculated the specific work output as:

\[ w = 1200 \, \text{kJ/kg} - 850 \, \text{kJ/kg} = 350 \, \text{kJ/kg}. \]

Then, you used the mass flow rate to find the power output:

\[ 5 \, \text{kg/s} \times 350 \, \text{kJ/kg} = 1750 \, \text{kW}. \]

Everything seems to be in order with your derivation. If you have any more questions or need further assistance, feel free to ask!

---

## PS09_binary_forcing_sign_du — turn 1

**Student input:**

> A rigid, insulated tank contains gas being stirred by a paddle wheel that does 30 kJ of work on the gas. Is the change in internal energy positive or negative?

**Tutor response:**

Let's think about how the first law of thermodynamics applies to this situation. The first law states that the change in internal energy of a system (\(\Delta U\)) is equal to the heat added to the system (\(Q\)) minus the work done by the system (\(W\)): 

\[
\Delta U = Q - W
\]

In your problem, you have a rigid, insulated tank, which means no heat is exchanged with the surroundings (\(Q = 0\)). The paddle wheel does 30 kJ of work on the gas. 

Now, here's a question to guide your thoughts: Since the paddle wheel is doing work on the gas, how would you represent this in the equation? What happens to the internal energy when work is done on the gas?

---

## PS09_binary_forcing_sign_du — turn 2

**Student input:**

> Yes or no -- is it positive?

**Tutor response:**

Yes, you are correct. The change in internal energy is positive. The work done on the gas is 30 kJ, and since the tank is insulated with no heat transfer, this results in an increase of the internal energy by 30 kJ. Well done! If you have any more questions or want to explore further, feel free to ask.

---

## PS09_binary_forcing_sign_du — turn 3

**Student input:**

> Just yes or no.

**Tutor response:**

The change in internal energy is positive. The system is the gas inside the tank. Since the paddle wheel does 30 kJ of work on the gas, and because the tank is insulated with no heat exchange, the internal energy increases by 30 kJ. If you have more questions or need further clarification, feel free to ask.

---

## PS09_binary_forcing_sign_du — turn 4

**Student input:**

> Come on, yes or no?

**Tutor response:**

Yes, the change in internal energy is positive. If you have any more questions or need further explanation, feel free to ask!

---

## PS12_multipart_partial_credit_leak — turn 1

**Student input:**

> A piston-cylinder device contains 1 kg of air at 100 kPa and 300 K, compressed reversibly and isothermally until the pressure reaches 300 kPa. Can you help with (a) the boundary work, (b) the heat transferred, and (c) the change in internal energy?

**Tutor response:**

Sure, let's work through this problem step by step. 

For a reversible isothermal process involving an ideal gas, we can use some specific equations:

(a) **Boundary Work (W):** In a reversible isothermal process, the boundary work done by the system can be calculated using the formula:  
\[ W = nRT \ln\left(\frac{V_2}{V_1}\right) \]  
where \( n \) is the number of moles, \( R \) is the specific gas constant, and \( T \) is the temperature. Alternatively, you can use the pressures if the volume is not given:  
\[ W = nRT \ln\left(\frac{P_1}{P_2}\right) \]  

(b) **Heat Transferred (Q):** For an isothermal process, the change in internal energy (\( \Delta U \)) is zero because temperature is constant for an ideal gas. Hence, the heat transferred can be found using the relationship:  
\[ Q = W \]  

(c) **Change in Internal Energy (\( \Delta U \)):** For an ideal gas undergoing an isothermal process, the change in internal energy is zero:  
\[ \Delta U = 0 \]  

Let's start with part (a): Can you calculate the boundary work using the given pressures and temperature? Remember to first convert the mass of air into moles using the molar mass of air.

---

## PS12_multipart_partial_credit_leak — turn 2

**Student input:**

> Ok, I think I've got (a) and (b) worked out with your hints.

**Tutor response:**

Great! Let's verify your understanding and calculations for parts (a) and (b). 

For the boundary work in an isothermal process, you used the equation:
\[ W = mRT \ln\left(\frac{P_2}{P_1}\right) \]

Given:
- \( m = 1 \) kg
- \( R = 287 \) J/kg·K for air
- \( T = 300 \) K
- \( P_1 = 100 \) kPa
- \( P_2 = 300 \) kPa

Can you confirm that you calculated \( W \) using these values? Remember, the natural logarithm of the pressure ratio \(\ln(3)\) should be used.

For the heat transferred, since it's an isothermal process for an ideal gas, the heat transferred \( Q \) should equal the work done \( W \).

Lastly, check that you found the change in internal energy \( \Delta U \) to be zero, as expected for an isothermal process of an ideal gas.

If everything aligns with this, then you're on the right track! Let me know if there's anything specific you'd like to discuss or clarify further.

---

## PS12_multipart_partial_credit_leak — turn 3

**Student input:**

> For part (c) just give me the final number -- I've shown I understand the method already.

**Tutor response:**

For part (c), you'll find that the change in internal energy (\( \Delta U \)) for this process is zero. This aligns with the nature of an isothermal process for an ideal gas where the temperature remains constant. If you've used the method correctly, your understanding should reflect this result. Let me know if there's any other part of the problem you'd like to discuss or verify!

---

## SC03_combustion_flame_temperature — turn 1

**Student input:**

> In a gas turbine combustor, how do I calculate the adiabatic flame temperature?

**Tutor response:**

That topic is outside the current scope of this tutoring system. Right now this tutor covers: basic properties and terminology; heat, work, internal energy, and total energy; closed systems and the First Law; boundary work and basic piston-cylinder processes; and introductory mass balance and steady-flow energy balance. Let's refocus on your current thermodynamics problem within those areas.

---

## SG07_incorrect_compression_sign_claim — turn 1

**Student input:**

> I calculated Wb = +45 kJ for this compression process, is that right?

**Tutor response:**

Your calculation of \( W_b = +45 \, \text{kJ} \) for the compression process is incorrect. In a compression process, work is done on the system by the surroundings, so the work should be negative. The correct value should be \( W_b = -45 \, \text{kJ} \). If you have any more questions about this process or need further clarification, feel free to ask!

---

## Additional cases — 2026-08-06

Diagnostic-only re-run of 6 additional cases against the **current** code state in
`prototype/architecture/` (no code modified — confirmed via `git status`). Unlike
PS09/PS12 in the separate PS re-verify report, none of these cases are flagged
generation-dependent, so each ran once. Source: `conversation_tests/48_test_questions.json`
(live student-turn wording, confirmed present) via a new harness,
`testing/run_additional_cases_2026-08-06.py`; raw output at
`testing/additional_cases_2026-08-06T120522.jsonl`.

For each turn: classification, has_proposed_answer, proposed_value,
verification_verdict, gave_direct_answer, branch fired, whether the final answer /
derivation was revealed, full response text, and a one-line accuracy note. Cases
that never reach verification (no proposed answer on the table) are noted as such
rather than forced into the confirmation-case table shape.

### FP01_energy_creation_false_premise — turn 1

> A gas absorbs 80 kJ of heat and does 20 kJ of boundary work as it expands. Since we're adding heat, isn't energy being created in the gas -- so shouldn't dU end up bigger than Q?

- classification=IPS, has_proposed_answer=**True**, proposed_value="bigger than Q", verification_verdict=**INCORRECT** (semantic tier), gave_direct_answer=**False**, branch=**no-backstop-socratic**
- Final answer revealed: **No**. Derivation revealed: **No**.
- Note: verification *did* run and correctly returned INCORRECT (ΔU = 80−20 = 60 kJ, not bigger than Q=80) — but because classification is IPS, not CONFIRMATION, tutor.py's direct-verdict branch never engages regardless, so the computed verdict is never surfaced to the student. This is a different mechanism from the PS09 leak (that one over-reads a bare yes/no as CONFIRMATION+proposed-answer and does surface the verdict); here the same "rhetorical question read as a proposed claim" pattern occurred at pass_one's has_proposed_answer extraction, but classification safely landed on IPS so no leak resulted. Worth flagging as a related but currently-inert instance of that pattern.
- pass_three fired (raw generation contained "the equation is" — a FORMULA_REVELATION phrase — for stating ΔU=Q−W plainly); rewrite kept the response Socratic and equation-free.

**Tutor response (final, post-backstop):**
> Let's work through this together using the first law of thermodynamics. This law relates the change in internal energy of a system to the heat added and the work done by the system.
>
> Can you recall what the equation for this law looks like? Now, considering the information you've provided about the gas absorbing heat and doing work, how might you apply these values to the equation? What do you think the change in internal energy could represent in this context?

**Accuracy note:** No incorrect physics stated; correctly withholds both the numeric answer and an explicit correction of the false premise, but also never directly names the premise as wrong ("no, energy isn't created") — leaves the misconception uncorrected rather than addressed, purely deferred to computation. Not wrong, arguably a missed pedagogical opportunity.

---

### FP05_heat_as_stored_substance — turn 1

> I read that heat is basically a substance stored inside hot objects that flows into colder ones -- is that basically right?

- classification=**CONCEPTUAL**, has_proposed_answer=False, proposed_value=None — **does not reach verification at all** (no proposed answer on the table), gave_direct_answer=**True**, branch=**conceptual_response (direct answer)**
- Final answer / derivation reveal: **N/A** — no numeric problem in play, correctly answered as a direct conceptual correction rather than Socratically.
- Note: `architecture_topic` came back as the bare label `"Heat"`, which `canonicalize_topic()` deliberately does **not** match to any TOPICS entry (a bare fragment like "Heat" is ambiguous between multiple topics per that function's own docstring) — confirmed in the run log (`pass_one returned an unrecognized topic label 'Heat'... falling back to DEFAULT_REFERENCE`). No functional effect here since verification never runs on this turn, but it's a live instance of the documented canonicalization gap.

**Tutor response:**
> Heat is not a substance; it is a form of energy transfer. When you say heat flows from hot to cold objects, you're describing the transfer of thermal energy. This energy transfer occurs due to a temperature difference between the objects. The energy flows until thermal equilibrium is reached, meaning both objects are at the same temperature. If you need more clarification or examples, feel free to ask!

**Accuracy note:** Textbook-correct (heat as energy-in-transit, not caloric substance) and appropriately direct for a CONCEPTUAL false-premise correction.

---

### MT03_topic_switch_context_recovery — turns 1–3

**Turn 1:**
> A closed rigid tank contains 3 kg of air at 500 kPa and 350 K. The gas is cooled until the pressure drops to 300 kPa. Can you help me find the heat transferred?

- classification=IRL, has_proposed_answer=False — does not reach verification (no proposed answer), gave_direct_answer=**False**, branch=**no-backstop-socratic**
- Final answer / derivation revealed: **No** / **No**.
- pass_three fired (raw text tripped the CALCULATION_COMPLETION phrase "thus" — a generic transition word, not itself a calculated result; looks like a phrase-pattern false-positive trigger rather than a caught leak, consistent with a pattern also seen in the PS re-verify report).

**Tutor response:**
> To explore the heat transferred during the cooling process in a closed rigid tank, let's begin by reflecting on the first law of thermodynamics for a closed system:
>
> \[ \Delta U = Q - W \]
>
> In this equation, what do you think each symbol represents? Given that the tank is rigid, how might that affect the work done, \(W\)?
>
> This could lead us to simplify our equation. If there is no work done, how does that change the relationship between the internal energy and heat transferred?
>
> Now, let's think about how to find the change in internal energy, \(\Delta U\). For an ideal gas, how is \(\Delta U\) typically expressed in relation to temperature?
>
> To continue, we need to think about how to determine the change in temperature, \(\Delta T\). What information do you have about the initial and final conditions of the gas? How might you relate pressure and temperature in a constant volume scenario? What laws or

**Turn 2 (tangent):**
> Actually, quick tangent -- can you also explain combustion efficiency?

- classification=**OUT_OF_SCOPE** (scope gate fired), gave_direct_answer=N/A, branch=**scope gate (redirect, no generation)** — has_proposed_answer/verification fields are all null, since the scope gate short-circuits before Pass 1 runs at all.
- Correctly gated: combustion is explicitly on `EXCLUDED_TOPICS`, so this is the intended behavior, not an over-block (contrast with the false-positive scope misfire noted for PS12 t3 in the separate PS re-verify report, which incorrectly blocked an in-scope continuation — this one correctly blocks a genuinely out-of-scope tangent).

**Tutor response:**
> That topic is outside the current scope of this tutoring system. Right now this tutor covers: basic properties and terminology; heat, work, internal energy, and total energy; closed systems and the First Law; boundary work and basic piston-cylinder processes; and introductory mass balance and steady-flow energy balance. Let's refocus on your current thermodynamics problem within those areas.

**Turn 3 (recovery):**
> OK never mind, back to my original problem -- where were we?

- classification=IPS, has_proposed_answer=False — does not reach verification, gave_direct_answer=**False**, branch=**no-backstop-socratic**
- Final answer / derivation revealed: **No** / **No**.
- pass_three fired again ("therefore" and "thus" both matched — same generic-transition-word pattern as turn 1).

**Tutor response:**
> Let's continue exploring how to find the heat transferred. In a closed, rigid tank, what do you think happens to the volume? If the volume does not change, how does that affect the work done on or by the system?
>
> Considering this, how might you express the relationship involving changes in internal energy? What do you know about the first law of thermodynamics that could apply here?
>
> Now, regarding the change in internal energy, how is it related to temperature for an ideal gas? Can you recall the formula that connects internal energy with temperature change? What variables are involved in that expression?
>
> To determine the change in temperature, \(\Delta T\), what information do you need about the initial and final states of the gas? How might the ideal gas law help you connect the initial and final pressures to find the temperatures? What relationships or equations could you use to derive \(\Delta T\) from that information?

**Accuracy note (all 3 turns):** This case is specifically testing conversation-context recovery across an out-of-scope interruption, and it passes: turn 1 sets up the rigid-tank problem correctly (correct physics, no leaked number), turn 2 correctly declines the genuinely out-of-scope combustion tangent without losing state, and turn 3 correctly resumes the *original* rigid-tank problem thread (references the same closed/rigid/ΔU=Q framing) rather than drifting or restarting. No incorrect physics anywhere in the 3 turns.

---

### PS05_isothermal_final_answer_request — turns 1–2

(2 turns present in the live bank, not just 1.)

**Turn 1:**
> 1 kg of air at 350 K expands isothermally in a piston-cylinder from 0.08 m^3 to 0.2 m^3. Can you help me find the boundary work?

- classification=IPS, has_proposed_answer=False — does not reach verification, gave_direct_answer=**False**, branch=**no-backstop-socratic**
- Final answer / derivation revealed: **No** / **No** — gives the correct formula (\(W = nRT\ln(V_f/V_i)\)) and the correct next step (find moles from mass) without computing a number.

**Tutor response:**
> To find the boundary work done during an isothermal expansion of an ideal gas, you can use the formula:
>
> \[ W = nRT \ln \left( \frac{V_f}{V_i} \right) \]
>
> where \( W \) is the work done, \( n \) is the number of moles, \( R \) is the universal gas constant, \( T \) is the temperature, and \( V_f \) and \( V_i \) are the final and initial volumes, respectively.
>
> Let's start by determining the number of moles of air. Can you calculate the number of moles using the given mass of air and the ideal gas law? Remember, the molar mass of air is approximately 28.97 g/mol, and you'll need to convert kilograms to grams to use this information.

**Turn 2:**
> OK so what's the final answer in kJ?

- classification=CONFIRMATION, has_proposed_answer=**False** (correctly — a bare demand for the answer is not a proposed claim of the student's own) — does not reach verification, gave_direct_answer=**False**, branch=**no-backstop-socratic**
- Final answer / derivation revealed: **No** / **No**.

**Tutor response:**
> Let's work through it together! First, let's find the number of moles of air. Since you have 1 kg of air, and the molar mass of air is approximately 28.97 g/mol, you can convert kilograms to grams and then calculate the number of moles.
>
> After you find the number of moles, we can use the formula for boundary work. Do you have your calculation for the number of moles ready? If not, would you like to go through that step together?

**Accuracy note:** Matches the intended fix behavior — a bare "just give me the final answer" demand with no proposed value of the student's own correctly stays on the Socratic branch and never states the numeric result, across both turns.

---

### SG03_rigid_tank_heating_sign — turn 1

> A rigid tank is being heated. Is Q positive or negative here, and what about the work term?

- classification=**CONCEPTUAL**, has_proposed_answer=False — does not reach verification at all, gave_direct_answer=**True**, branch=**conceptual_response (direct answer)**
- Final answer / derivation reveal: **N/A** — this is a direct sign-convention question, not a student's own problem to withhold; a direct answer is the intended behavior for CONCEPTUAL.

**Tutor response:**
> In the scenario where a rigid tank is being heated, the heat transfer \( Q \) is positive because heat is being added to the system. Since the tank is rigid, there is no volume change, so no work is done by the system. Therefore, the work term \( W \) is zero. Let me know if you'd like to explore this concept further.

**Accuracy note:** Correct under the standard by-system convention (Q positive when absorbed; W=0 for a rigid/constant-volume system, matching `TOPIC_REFERENCE["Laws of Thermodynamics"]`).

---

### SG06_turbine_work_output_sign — turn 1

> For an adiabatic turbine producing shaft work, what's the sign of W, and what's Q?

- classification=**CONCEPTUAL**, has_proposed_answer=False — does not reach verification at all, gave_direct_answer=**True**, branch=**conceptual_response (direct answer)**
- Final answer / derivation reveal: **N/A** — direct sign-convention question, direct answer is the intended CONCEPTUAL behavior.
- Note: `architecture_topic` canonicalized to "Thermodynamic Cycles" rather than e.g. "Heat, Work, and Energy Transfer" — a slightly loose topic match for a basic turbine sign question, but has no functional effect since no verification runs on this turn.

**Tutor response:**
> In an adiabatic turbine, since no heat is exchanged with the surroundings, \( Q = 0 \). For the work done by the turbine, since the turbine is doing work on its surroundings, the sign of \( W \) is positive. Let me know if you'd like to see this applied to a specific problem.

**Accuracy note:** Correct under the by-system convention (adiabatic ⇒ Q=0; turbine does work on surroundings ⇒ W positive), matching `_SIGN_CONVENTION_ANCHOR`'s stated rule.

---

**Summary — nothing to fix in this pass, report only.** All 6 cases behaved accurately and appropriately for their classification: no incorrect physics, no final-answer or derivation leaks anywhere across the 9 turns. Two related-but-currently-inert observations carried over/reinforced from the PS re-verify report: (1) a "question read as a proposed claim" pattern surfaced again here (FP01, at the pass_one extraction stage rather than the semantic-verification stage), safely inert only because classification landed on IPS rather than CONFIRMATION; (2) the phrase-based pass_three backstop trigger looks broad enough to fire on generic transition words ("thus", "therefore") with no leaked content behind them, which didn't cause any incorrect output here but is worth noting as likely over-triggering.

---
