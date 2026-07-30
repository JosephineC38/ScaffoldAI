import architecture.two_pass_engine as tpe
from architecture.scope_check import REDIRECT_MESSAGE
from architecture.two_pass_engine import generate_response


def test_generate_response_short_circuits_on_out_of_scope(monkeypatch):
  monkeypatch.setattr(tpe, "check_scope", lambda user_input, conversation_history: False)

  def fail_if_called(*args, **kwargs):
    raise AssertionError("pass_one should not run when the scope gate rejects the turn")

  monkeypatch.setattr(tpe, "pass_one", fail_if_called)
  monkeypatch.setattr(tpe, "MODE_HANDLERS", {**tpe.MODE_HANDLERS, "Tutor": fail_if_called})
  pass_three_called = []
  monkeypatch.setattr(tpe, "pass_three", lambda *a, **k: pass_three_called.append(True))

  response_text, topic, diagnostics = generate_response("Explain psychrometrics to me.", [], "Tutor")

  assert response_text == REDIRECT_MESSAGE
  assert topic == "Out of Scope"
  assert diagnostics["classification"] == "OUT_OF_SCOPE"
  assert pass_three_called == []  # redirect is a fixed string, never routed through sanitization


def test_generate_response_calls_check_scope_on_every_turn(monkeypatch):
  calls = []

  def spy_check_scope(user_input, conversation_history):
    calls.append((user_input, len(conversation_history)))
    return True  # in scope -- let the rest of the pipeline run normally

  monkeypatch.setattr(tpe, "check_scope", spy_check_scope)

  content = '{"topic": "Laws of Thermodynamics", "classification": "IPS", "reasoning_gap": "g", "misconception": null}'

  def fake_create(**kwargs):
    from tests.conftest import fake_openai_response
    return fake_openai_response(content, prompt_tokens=10, completion_tokens=5)

  monkeypatch.setattr(tpe.client.chat.completions, "create", fake_create)
  monkeypatch.setattr(tpe, "MODE_HANDLERS", {**tpe.MODE_HANDLERS, "Tutor": lambda *a, **k: ("stub", False)})

  history = [{"role": "user", "content": "prior turn"}, {"role": "assistant", "content": "prior reply"}]
  generate_response("A follow-up question", history, "Tutor")

  # confirms the gate runs per-turn (fed this turn's own history), not just on turn 1
  assert calls == [("A follow-up question", 2)]


def test_generate_response_runs_pass_one_when_in_scope(monkeypatch):
  monkeypatch.setattr(tpe, "check_scope", lambda user_input, conversation_history: True)

  pass_one_calls = []

  def spy_pass_one(user_input, conversation_history):
    pass_one_calls.append(user_input)
    return "Laws of Thermodynamics", '{"classification": "IPS", "reasoning_gap": "g", "misconception": null}'

  monkeypatch.setattr(tpe, "pass_one", spy_pass_one)
  monkeypatch.setattr(tpe, "MODE_HANDLERS", {**tpe.MODE_HANDLERS, "Tutor": lambda *a, **k: ("stub response", False)})

  response_text, topic, diagnostics = generate_response("Why is dU = Q - W?", [], "Tutor")

  assert pass_one_calls == ["Why is dU = Q - W?"]
  assert response_text == "stub response"
  assert diagnostics["classification"] == "IPS"
