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
  "the word done is",
  "the heat transfer is",
  "the entropy is",
  "the enthalpy is",
  "the effeciency is",
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