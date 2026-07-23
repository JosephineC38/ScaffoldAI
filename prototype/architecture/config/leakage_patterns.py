DIRECT_ANSWER_DECLARATIONS = [
  "the answer is",
  "the solution is",
  "the result is",
  "the final answer is",
  "the correct answer is",
  "the value is",
  "the answer would be"
]

THERMO_SPECIFIC = [
  "the temperature is",
  "the pressure is",
  "the work done is",
  "the heat transfer is",
  "the entropy is",
  "the enthalpy is",
  "the efficiency is",
  "the quality is",
]

CALCULATION_COMPLETION = [
  "therefore",
  "thus",
  "which gives us",
  "which gives",
  "this gives",
  "solving for",
  "we get",
  "we find",
  "we find",
  "we obtain",
  "this yields",
  "plugging in",
  "substituting"
]

FORMULA_REVELATION = [
  "using the equation",
  "applying the formula",
  "the formula is",
  "the equation is",
  "the equation becomes",
  "rearranging gives",
  "rearranging yields"
]

ALL_PHRASES = (
  DIRECT_ANSWER_DECLARATIONS
  + THERMO_SPECIFIC
  + CALCULATION_COMPLETION
  + FORMULA_REVELATION
)

# --- Naive numeric-value detector (pattern-matching only, no scoping to ---
# --- "novel"/student-given values — that context-aware version is a     ---
# --- separate future task, deliberately not attempted here).            ---
import re

_NUMERIC_UNIT_TOKENS = (
  "kJ", "MJ", "GJ", "kPa", "MPa", "GPa", "Pa", "J",
  "kmol", "mol", "kg", "bar", "atm", "kW", "rpm",
  "m/s", "m^3", "m3", "m³", "°C", "°F", "K",
)
_UNIT_TOKENS_BY_LENGTH = sorted(_NUMERIC_UNIT_TOKENS, key=len, reverse=True)

# number (optional sign/decimal) followed by a known physics unit token,
# e.g. "50 kJ", "-50kPa", "300 K"
NUMERIC_UNIT_PATTERN = re.compile(
  r'-?\d+(?:\.\d+)?\s*(?:' + '|'.join(re.escape(u) for u in _UNIT_TOKENS_BY_LENGTH) + r')\b',
  re.IGNORECASE,
)

# variable-equals-number, e.g. "Q = -50", "W=200"
VARIABLE_EQUALS_NUMBER_PATTERN = re.compile(r'\b[A-Za-z]+\s*=\s*-?\d+(?:\.\d+)?')

# a standalone explicitly-signed number with no unit/variable attached,
# e.g. "-50" — the sign is the only naive signal that it's a computed
# value rather than an incidental count/label in the surrounding text
SIGNED_BARE_NUMBER_PATTERN = re.compile(r'(?<![\w.])[+-]\d+(?:\.\d+)?(?!\w)')

NUMERIC_VALUE_PATTERNS = (
  NUMERIC_UNIT_PATTERN,
  VARIABLE_EQUALS_NUMBER_PATTERN,
  SIGNED_BARE_NUMBER_PATTERN,
)
