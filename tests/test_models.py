from ghmonitor.models import *


def test_event_types_from_str():
    assert EventType.PUSH == EventType.from_str("PushEvent")
    assert EventType.ISSUE == EventType.from_str("IssuesEvent")
    assert EventType.PULL_REQUEST == EventType.from_str("PullRequestEvent")
    try:
        EventType.from_str("foobar")
    except Exception as e:
        assert isinstance(e, UnknownEvent)


def test_event_parser_returns_event():
    print("Testing data parser")
    a = {"id": "222", "type": "PushEvent", "repo": {"name": "a"}}
    b = {"id": "222", "tpe": "PushEvent", "repo": {"name": "a"}}
    assert isinstance(Event.from_dict(a), Event)
    assert Event.from_dict(b) is None


def test_events_comparison():
    e0 = Event()
    e1 = Event()
    assert e0 == e1
    e0.repo = 'a'
    assert not(e0 == e1)
    e1.repo = 'a'
    e0.id = 1
    e1.id = 1
    e0.type = EventType.PUSH
    e1.type = EventType.PUSH
    assert e0 == e1
