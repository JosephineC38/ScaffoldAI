import os
import json
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import prompt_builder
from config.thermo_topics import TOPICS

dotenv_path = Path(__file__).parents[2] / ".env"
load_dotenv(dotenv_path)

API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)

user_input = input("Enter question: ")
conversation_history = []

def classify_topic(user_input: str) -> str:
  classify_topic_prompt = f"""
    Given the user input, classify which topic it falls under using ONLY the given topic names

    Topics:
    {chr(10).join(TOPICS)}

    User input: {user_input}
  """

  classify_topic_analysis = client.chat.completions.create(
    model = "gpt-4o-mini", # $0.15/million input tokens, $0.60/million output tokens
    messages=[
      {"role": "user",
       "content": classify_topic_prompt}
    ],
    max_tokens=20,
    temperature=0.0
  )

  return classify_topic_analysis.choices[0].message.content.strip()

topic = classify_topic(user_input)

def pass_one(user_input: str, topic: str) -> str:
  pass_one_prompt = f"""
    topic: {topic}
    student input: {user_input} 

    Respond with this exact JSON format:
    {{
      "classification": "IPS" or "IRL",
      "reasoning_gap": "brief description of what the student is missing/asking",
      "misconception": "specific misconception if one exists, otherwise null"
    }}
    
    Classification rules:
    - IPS: student has encountered this concept before but is making an execution error
    - IRL: concept is new to the student

    
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
  )

  return pass_one_analysis.choices[0].message.content

def pass_two(user_input: str, pass_one_diagnosis: str, topic: str, conversation_history: list) -> str:
  system_prompt = prompt_builder.prompt_builder()
  
  pass_two_prompt = f"""
    topic: {topic}
    diagnoistic context (do not reveal this to the student): {pass_one_diagnosis}
    original student input message: {user_input}

    Using the diagnostic context above to inform your response, generate a response to help guide the student. 

    Do not reveal the diagnosis or the correct answer.
    """

  messages = [{"role": "system", "content": system_prompt}]
  messages += conversation_history[-12:] # conversation memory holds the previous 12 messages
  messages.append({"role": "user", "content": pass_two_prompt})

  pass_two_analysis = client.chat.completions.create(
    model = "gpt-4o", # $2.50/million input tokens, $10.00/million output tokens
    messages=messages, # api responds to the most recent index
    max_tokens=200,
    temperature=0.7 # higher creativity output -> offers more variation for user
  )

  return pass_two_analysis.choices[0].message.content

def generate_response(user_input: str, topic, conversation_history) -> str:
  diagnosis = pass_one(user_input, topic)
  system_response = pass_two(user_input, diagnosis, topic, conversation_history)

  return system_response

response = generate_response(user_input, topic, conversation_history)

print(response)
