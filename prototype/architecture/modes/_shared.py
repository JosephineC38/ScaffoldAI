from architecture.two_pass_engine import _call_pass_two_model


def conceptual_response(user_input: str, diagnosis: str, topic: str, conversation_history: list, system_prompt: str) -> str:
  pass_two_prompt = f"""
      topic: {topic}
      diagnostic context: {diagnosis}
      original student input message: {user_input}

      The student is asking a direct factual or definitional question (a law, definition, or formula) with no problem context to work through. Use the diagnostic context only to calibrate depth and framing, not to decide whether to answer.

      Give a clear, correct, and concise answer. State the answer directly instead of responding with a question. Do not end your response with a question — if you want to invite further engagement, do it as a statement (e.g. "Let me know if you'd like to see this applied to a problem."), not a question.
      """

  return _call_pass_two_model(system_prompt, conversation_history, pass_two_prompt)
