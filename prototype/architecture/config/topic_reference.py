# Static, authoritative reference formulas/conventions per topic, used by the
# semantic verification tier (architecture.verification) to check a student's
# derivation without depending on conversation history. Keep this independent
# of any single conversation so it can't inherit conversational drift.

TOPIC_REFERENCE = {
    "Laws of Thermodynamics": (
        "First law: delta U = Q - W. Q is heat added TO the system (positive if "
        "absorbed by the system, negative if rejected/lost by the system). W is "
        "work done BY the system (positive if the system does work on the "
        "surroundings, negative if work is done on the system by the surroundings). "
        "For a rigid/constant-volume system, W = 0, so delta U = Q."
    ),
    "Heat, Work, and Energy Transfer": (
        "Boundary work at constant pressure: W = P * delta V. Work done BY a "
        "system is positive in delta U = Q - W; work done ON a system is negative "
        "W in that same equation. Heat flows from hot to cold."
    ),
    "Entropy and Exergy": (
        "For a reversible heat transfer at constant temperature T (Kelvin): "
        "delta S = Q / T. Q is positive if heat is absorbed by the system, "
        "negative if heat is rejected/lost by the system, so delta S has the same "
        "sign as Q in this formula."
    ),
    "Thermodynamic Cycles": (
        "Carnot efficiency: eta = 1 - Tc/Th (temperatures in Kelvin, Th = hot "
        "reservoir, Tc = cold reservoir). Carnot refrigerator COP: "
        "COP = Tc / (Th - Tc). Carnot heat pump COP: COP = Th / (Th - Tc)."
    ),
    "Open vs Closed Systems": (
        "Closed systems exchange energy but not mass with the surroundings; open "
        "systems (control volumes) exchange both. Steady-flow energy balance for "
        "a turbine, neglecting kinetic/potential energy: "
        "power = mass_flow_rate * (h_in - h_out), where h is specific enthalpy."
    ),
    "Psychrometrics": (
        "Relative humidity RH = Pv / Psat, where Pv is the actual vapor pressure "
        "and Psat is the saturation vapor pressure at that temperature. Humidity "
        "ratio (specific humidity) omega = mass of water vapor / mass of dry air."
    ),
    "Combustion and Thermochemistry": (
        "Total heat released by combustion = mass of fuel * heating value. "
        "Useful work output of an engine = thermal efficiency * total heat "
        "released from the fuel."
    ),
    "Equations of State and Real Gases": (
        "Ideal gas law: P * V = n * R * T (R = 8.314 J/mol*K when using SI units "
        "with n in moles). Boyle's law (constant temperature and moles): "
        "P1 * V1 = P2 * V2."
    ),
    "Properties of Pure Substances and Phase Changes": (
        "Latent heat (phase change, no temperature change): "
        "Q = mass * latent heat of the phase change. Sensible heat (temperature "
        "change, no phase change): Q = mass * specific heat * delta T."
    ),
}

DEFAULT_REFERENCE = (
    "No specific reference formula is on file for this topic; reason from "
    "standard undergraduate thermodynamics conventions."
)


def get_reference(topic: str) -> str:
    return TOPIC_REFERENCE.get(topic, DEFAULT_REFERENCE)
