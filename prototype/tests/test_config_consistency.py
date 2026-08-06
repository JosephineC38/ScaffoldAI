from architecture.config.thermo_topics import TOPICS
from architecture.config.topic_reference import TOPIC_REFERENCE, DEFAULT_REFERENCE, get_reference
from architecture.config.modes import MODES
from architecture.two_pass_engine import MODE_HANDLERS, _topic_word_key, canonicalize_topic


def test_topics_and_topic_reference_keys_match_exactly():
  assert set(TOPICS) == set(TOPIC_REFERENCE.keys())


def test_modes_and_mode_handlers_keys_match_exactly():
  assert set(MODES) == set(MODE_HANDLERS.keys())


def test_get_reference_returns_default_for_unknown_topic():
  assert get_reference("Not A Real Topic") == DEFAULT_REFERENCE


def test_get_reference_returns_real_entry_for_every_known_topic():
  for topic in TOPICS:
    assert get_reference(topic) == TOPIC_REFERENCE[topic]
    assert get_reference(topic) != DEFAULT_REFERENCE


def test_no_two_topics_collide_on_their_canonicalization_key():
  """canonicalize_topic() matches on an order-independent word key, so two
  TOPICS entries sharing a key would be mutually ambiguous and one would
  silently shadow the other. two_pass_engine asserts this at import; this
  makes it a visible invariant for anyone adding a topic."""
  keys = {}
  for topic in TOPICS:
    key = _topic_word_key(topic)
    assert key not in keys, f"{keys[key]!r} and {topic!r} share a canonicalization key"
    keys[key] = topic


def test_every_topic_canonicalizes_to_itself():
  for topic in TOPICS:
    assert canonicalize_topic(topic) == topic
