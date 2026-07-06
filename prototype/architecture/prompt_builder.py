import json
from pathlib import Path

base_dir = Path(__file__).parent
config_path = base_dir / "config" / "system_prompt_components.json"

with open(config_path, 'r') as rules_file:
  data = json.load(rules_file)

# turns system_prompt_components.json into one string
def prompt_builder():
  extracted_text = []

  for item in data["components"]:
    text_content = item.get("text")
    component_content = item.get("component")

    extracted_text.append(component_content.upper() + ": ")

    if isinstance(text_content, list):
      extracted_text.append(", ".join(text_content))
    
    elif isinstance(text_content, str):
      extracted_text.append(text_content)

  return " ".join(extracted_text)

    