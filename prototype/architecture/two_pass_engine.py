import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
import prompt_builder
import leakage_check
import leakage_patterns

dotenv_path = Path(__file__).parents[2] / ".env"
load_dotenv(dotenv_path)

API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)

user_input = ""

def pass_one(user_input: str) -> str:
  pass_one_analysis = client.chat.completions.create(
    model = "gpt-4o-mini",
    messages=[
      {"role": "user",
       "content": f"""
       student input: {user_input} 

       your job is to understand the reasoning gap in the student's thinking. 
       
       Do the following: 
       1. identify what concept or step the student is misunderstanding or missing. 
       2. identify any specfic misconceptions present if one exists. 
       
       Do NOT include the correct answer. Respond only with structured diagnostic. Your output will not be shown to the student
       """}
    ],
    max_tokens=300,
    temperature=0.1,
  )

  return pass_one_analysis

def pass_two(user_input: str, pass_one_diagnosis: str) -> str:
  pass_two_analysis = client.chat.completions.create(
    model = "gpt-4o",
    messages=[
      {"role": "assistant",
       "content": f"""
       diagnoistic context (do not reveal this to the student): {pass_one_diagnosis}
       original student input message: {user_input}

       Using the diagnostic context above to inform your response, generate a response to help guide the student. 

       Do not reveal the diagnosis or the correct answer.

       """
       }
    ],
    max_tokens=200,
    temperature=0.7
  )

  return pass_two_analysis

def generate_response(user_input: str) -> str:
  diagnosis = pass_one(user_input)
  system_response = pass_two(user_input, diagnosis)

  return system_response






