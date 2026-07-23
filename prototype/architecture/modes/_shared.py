import os
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from architecture.cost_log import log_cost_event

dotenv_path = Path(__file__).parents[3] / ".env"
load_dotenv(dotenv_path)

API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)


def _call_pass_two_model(system_prompt: str, conversation_history: list, pass_two_prompt: str, max_tokens: int = 200, mode: str = "", conversation_id: str = "", turn: str = "") -> str:
  messages = [{"role": "system", "content": system_prompt}]
  messages += conversation_history
  messages.append({"role": "user", "content": pass_two_prompt})

  t0 = time.perf_counter()
  response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=messages,
    max_tokens=max_tokens,
    temperature=0.7
  )
  log_cost_event("pass2_response", "gpt-4o-mini", response, time.perf_counter() - t0, mode=mode, conversation_id=conversation_id, turn=turn)
  return response.choices[0].message.content


def _verification_context(verification: dict) -> str:
  if not verification:
    return ""
  return f"""
      Independent verification result (for your own awareness — whether/how you
      may state this outright is still governed by your other instructions):
      verdict={verification['verdict']}, checked via {verification['tier']} tier,
      correct_value={verification.get('correct_value')}, reasoning={verification.get('reasoning')}
      """


def conceptual_response(user_input: str, diagnosis: str, topic: str, conversation_history: list, system_prompt: str, mode: str = "", conversation_id: str = "", turn: str = "") -> str:
  pass_two_prompt = f"""
      topic: {topic}
      diagnostic context: {diagnosis}
      original student input message: {user_input}

      The student is asking a direct factual or definitional question (a law, definition, or formula) with no problem context to work through. Use the diagnostic context only to calibrate depth and framing, not to decide whether to answer.

      Give a clear, correct, and concise answer. State the answer directly instead of responding with a question. Do not end your response with a question — if you want to invite further engagement, do it as a statement (e.g. "Let me know if you'd like to see this applied to a problem."), not a question.
      """

  return _call_pass_two_model(system_prompt, conversation_history, pass_two_prompt, mode=mode, conversation_id=conversation_id, turn=turn)
