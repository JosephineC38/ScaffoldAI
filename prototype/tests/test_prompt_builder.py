from architecture.prompt_builder import prompt_builder, data


def test_prompt_builder_returns_non_empty_string():
  result = prompt_builder()
  assert isinstance(result, str)
  assert len(result) > 0


def test_prompt_builder_is_deterministic_across_calls():
  assert prompt_builder() == prompt_builder()


def test_prompt_builder_includes_every_component_header():
  result = prompt_builder()
  for item in data["components"]:
    header = item["component"].upper() + ": "
    assert header in result
    text_content = item.get("text")
    expected_text = ", ".join(text_content) if isinstance(text_content, list) else text_content
    assert expected_text in result
