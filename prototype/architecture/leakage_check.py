import os
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from architecture.config.leakage_patterns import ALL_PHRASES
from architecture.cost_log import log_cost_event

dotenv_path = Path(__file__).parents[2] / ".env"
load_dotenv(dotenv_path)

API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)

# returns true if text contains a phrase in leakage_patterns.py
def contains_phrase(text: str) -> bool:
  text_lower = text.lower()
  return any(phrase in text_lower for phrase in ALL_PHRASES)

def pass_three(leaked_response: str, topic: str, conversation_id: str = "", turn: str = "") -> str: # only called if output detects answer leakage
  pass_three_prompt = f""" 
    The following tutoring response contains direct answers or answer-revealing 
    language that must be removed. Rewrite it to preserve the Socratic scaffolding 
    intent — the guiding questions, the reasoning prompts — but strip any 
    language that reveals or implies the correct answer.

    Original response:
    {leaked_response}

    Topic: {topic}

    Do not confirm or deny correctness. Do not include calculations or final values.
    Return only the rewritten response.
  """
  t0 = time.perf_counter()
  pass_three_response = client.chat.completions.create(
    model = "gpt-4o-mini", # $0.15/million input tokens, $0.60/million output tokens
    messages=[
      {"role": "user",
       "content": pass_three_prompt}
    ],
    max_tokens=200,
    temperature=0.7
  )
  log_cost_event("leakage_sanitize", "gpt-4o-mini", pass_three_response, time.perf_counter() - t0, conversation_id=conversation_id, turn=turn)

  return pass_three_response.choices[0].message.content
