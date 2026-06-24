from prototype.architecture.config.leakage_patterns import ALL_PHRASES

system_output = "hello the answer is" # current place holder for system output

def contains_phrase(text: str) -> bool:
  text_lower = text.lower()
  return any(phrase in text_lower for phrase in ALL_PHRASES)

has_flag = contains_phrase(system_output)
