import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

try:
    from .prompt_builder import prompt_builder
    from .config.thermo_topics import TOPICS
except ImportError:
    from prompt_builder import prompt_builder
    from config.thermo_topics import TOPICS

dotenv_path = Path(__file__).parents[2] / ".env"
load_dotenv(dotenv_path)

API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)

def pass_one(user_input: str):
  pass_one_prompt = f"""
    student input: {user_input}

    Respond with this exact JSON format:
    {{
      "topic": "one of: {', '.join(TOPICS)}",
      "classification": "IPS", "IRL", or "CONCEPTUAL"
      "reasoning_gap": "brief description of what the student is missing/asking",
      "misconception": "specific misconception if one exists, otherwise null"
    }}

    Classification rules:
    - IPS: student has encountered this concept before but is making an execution error
    - IRL: concept is new to the student
    - CONCEPTUAL: student is asking for a definition, law, formula, or terminology directly, with no problem context, numeric values, or reference to their own attempt


    Do NOT include the correct answer. Respond only with structured diagnostic. Your output will not be shown to the student
    """

  pass_one_analysis = client.chat.completions.create(
    model = "gpt-4o-mini", # $0.15/million input tokens, $0.60/million output tokens
    messages=[
      {"role": "user",
       "content": pass_one_prompt}
    ],
    max_tokens=200,
    temperature=0.1, # low creativity output
    response_format={"type": "json_object"},
  )

  diagnosis = json.loads(pass_one_analysis.choices[0].message.content)
  topic = diagnosis.pop("topic")

  return topic, json.dumps(diagnosis)

input = "I'm doing a piston-cylinder problem where the gas expands and I calculated the work as -500 J, but I think it should be positive since the gas is doing work on the surroundings. What am I doing wrong?"

topic, diagnosis = pass_one(input)
print(diagnosis)

def pass_two(user_input: str, pass_one_diagnosis: str, topic: str, conversation_history: list) -> str:
  system_prompt = prompt_builder()

  classification = json.loads(pass_one_diagnosis).get("classification")

  if classification == "CONCEPTUAL":
    pass_two_prompt = f"""
      topic: {topic}
      diagnostic context: {pass_one_diagnosis}
      original student input message: {user_input}

      The student is asking a direct factual or definitional question (a law, definition, or formula) with no problem context to work through. Use the diagnostic context only to calibrate depth and framing, not to decide whether to answer.

      Give a clear, correct, and concise answer. State the answer directly instead of responding with a question. Do not end your response with a question — if you want to invite further engagement, do it as a statement (e.g. "Let me know if you'd like to see this applied to a problem."), not a question.
      """
  else:
    pass_two_prompt = f"""
      topic: {topic}
      diagnoistic context (do not reveal this to the student): {pass_one_diagnosis}
      original student input message: {user_input}

      Using the diagnostic context above to inform your response, generate a response to help guide the student.

      Do not reveal the diagnosis or the correct answer.
      """

  messages = [{"role": "system", "content": system_prompt}]
  messages += conversation_history
  messages.append({"role": "user", "content": pass_two_prompt})

  pass_two_analysis = client.chat.completions.create(
    model = "gpt-4o-mini", # $0.15/million input tokens, $0.60/million output tokens
    messages=messages, # api responds to the most recent index
    max_tokens=200,
    temperature=0.7 # higher creativity output -> offers more variation for user
  )

  return pass_two_analysis.choices[0].message.content

def generate_response(user_input: str, conversation_history):
  topic, diagnosis = pass_one(user_input)
  system_response = pass_two(user_input, diagnosis, topic, conversation_history)

  return system_response, topic

response = generate_response(input, [])
# print(response)

def return_response(user_input):
  response, _ = generate_response(user_input, [])
  print(response)
  return response


