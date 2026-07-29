import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from architecture.testing.cost_tracker import turn_usage

dotenv_path = Path(__file__).parents[3] / ".env"
load_dotenv(dotenv_path)

API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=API_KEY)

CONVERSATION_HISTORY_WINDOW = 8  # last N messages (not exchanges) of conversation_history; shared by Pass 1 and Pass 2


class ResponseTruncatedError(RuntimeError):
  """Raised when a Pass 2 completion is cut off by max_tokens twice in a row
  (the original call and one same-prompt retry). At temperature=0.7, response
  length is a distribution, not a fixed value -- no max_tokens ceiling gives a
  hard guarantee, only better odds (see testing/CHANGELOG.md for the
  empirical data behind this). A single truncation is retried once since a
  second sample often lands under the cap; a second consecutive truncation is
  surfaced as a hard failure instead of letting a cut-off, mid-sentence
  response reach the student or the eval harness looking like a normal one."""


def _call_pass_two_model(system_prompt: str, conversation_history: list, pass_two_prompt: str, max_tokens: int = 200) -> str:
  messages = [{"role": "system", "content": system_prompt}]
  messages += conversation_history[-CONVERSATION_HISTORY_WINDOW:]
  messages.append({"role": "user", "content": pass_two_prompt})

  response = client.chat.completions.create(
    model="gpt-4o",
    messages=messages,
    max_tokens=max_tokens,
    temperature=0.7
  )
  turn_usage.record("gpt-4o", response.usage.prompt_tokens, response.usage.completion_tokens)

  if response.choices[0].finish_reason == "length":
    retry_response = client.chat.completions.create(
      model="gpt-4o",
      messages=messages,
      max_tokens=max_tokens,
      temperature=0.7
    )
    turn_usage.record("gpt-4o", retry_response.usage.prompt_tokens, retry_response.usage.completion_tokens)

    if retry_response.choices[0].finish_reason == "length":
      raise ResponseTruncatedError(
        f"Pass 2 completion (model=gpt-4o, max_tokens={max_tokens}) was truncated "
        f"twice in a row (finish_reason='length' on both the original call and the retry)."
      )
    response = retry_response

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


def conceptual_response(user_input: str, diagnosis: str, topic: str, conversation_history: list, system_prompt: str) -> str:
  pass_two_prompt = f"""
      topic: {topic}
      diagnostic context: {diagnosis}
      original student input message: {user_input}

      The student is asking a direct factual or definitional question (a law, definition, or formula) with no problem context to work through. Use the diagnostic context only to calibrate depth and framing, not to decide whether to answer.

      Give a clear, correct, and concise answer. State the answer directly instead of responding with a question. Do not end your response with a question — if you want to invite further engagement, do it as a statement (e.g. "Let me know if you'd like to see this applied to a problem."), not a question.
      """

  return _call_pass_two_model(system_prompt, conversation_history, pass_two_prompt, max_tokens=1000)
