import sys
from pathlib import Path
from types import SimpleNamespace

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # prototype/

import pytest


def fake_openai_response(content, prompt_tokens: int = 100, completion_tokens: int = 50):
  """Builds a stand-in for an OpenAI ChatCompletion response, matching the
  .choices[0].message.content / .usage.prompt_tokens / .usage.completion_tokens
  shape every call site in architecture/ reads from."""
  return SimpleNamespace(
    choices=[SimpleNamespace(message=SimpleNamespace(content=content))],
    usage=SimpleNamespace(prompt_tokens=prompt_tokens, completion_tokens=completion_tokens),
  )


@pytest.fixture
def make_openai_response():
  return fake_openai_response


@pytest.fixture(autouse=True)
def reset_turn_usage():
  from architecture.testing.cost_tracker import turn_usage
  turn_usage.reset()
  yield
  turn_usage.reset()
