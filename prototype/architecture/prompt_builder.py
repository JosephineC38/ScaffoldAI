import json

with open("system_prompt_components.json", 'r') as rules_file:
  data = json.load(rules_file)

extracted_text = []

for item in data["components"]:
  text_content = item.get("text")
  component_content = item.get("component")

  extracted_text.append(component_content.upper() + ":")

  if isinstance(text_content, list):
    extracted_text.append(", ".join(text_content))
  
  elif isinstance(text_content, str):
    extracted_text.append(text_content)
    