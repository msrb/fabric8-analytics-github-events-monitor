import logging

from enum import Enum

logger = logging.getLogger('Monitor')


class UnknownEvent(Exception):
    pass


class EventType(Enum):
    """
    Represent event types that we are interested in like new pull requests, issues, or comments
    """
    PUSH = 1
    PULL_REQUEST = 2
    ISSUE = 3

    @staticmethod
    def from_str(input_string):
        mapping = {
            "PushEvent": EventType.PUSH,
            "PullRequestReviewCommentEvent": EventType.PULL_REQUEST,
            "PullRequestEvent": EventType.PULL_REQUEST,
            "IssuesEvent": EventType.ISSUE,
        }
        try:
            return mapping[input_string]
        except KeyError:
            raise UnknownEvent


class Event:
    """
    Event structure that contains only information relevant for our use case.
    Also performs type check.
    """
    def __init__(self):
        self.id = None
        self.type = None
        self.repo = None

    def __str__(self):
        return "<Event id='{}', type='{}', repo='{}'>".format(self.id, self.type, self.repo)

    def __eq__(self, other):
        return (self.id, self.type, self.repo) == (other.id, other.type, other.repo)

    def __hash__(self):
        """
        https://docs.python.org/3/reference/datamodel.html#object.__hash__
        """
        return hash((self.id, self.type, self.repo))

    @staticmethod
    def from_dict(input_dict):
        """
        Filter the input dictionary and type check its members
        :param input_dict: JSON as a Python dictionary
        :return: Event object or None in case of unknown event type or other failure
        """
        ret = Event()
        try:
            ret.id = int(input_dict['id'])
            ret.type = EventType.from_str(input_dict['type'])
            ret.repo = input_dict['repo']['name']
            logger.debug(str(ret))
            return ret
        except ValueError:
            logger.error('Integer conversion failed')
            return None
        except UnknownEvent:
            return None
        except KeyError:
            logger.error('Input dictionary does not contain required keys')
            return None


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
