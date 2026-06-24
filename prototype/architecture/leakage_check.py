from prototype.architecture.config.leakage_patterns import ALL_PHRASES

system_output = "" # current place holder for system output

# returns true if system_output contains a phrase in leakage_patterns.py
def contains_phrase(text: str) -> bool:
  text_lower = text.lower()
  return any(phrase in text_lower for phrase in ALL_PHRASES)

has_flag = contains_phrase(system_output)
