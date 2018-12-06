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
            EventType.PUSH: ["PushEvent"],
            EventType.PULL_REQUEST: ["PullRequestReviewCommentEvent", "PullRequestEvent"],
            EventType.ISSUE: ["IssuesEvent"]
        }
        for k, v in mapping.items():
            if input_string in v:
                return k
        raise UnknownEvent


class Event(object):
    """
    Event structure that contains only information relevant for our use case.
    Also performs type check.
    """
    def __init__(self):
        self.id = None
        self.type = None

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


def test_event_parser_returns_event():
    print("Testing data parser")
    a = {"id": "222", "type": "PushEvent", "repo": {"name": "a"}}
    b = {"id": "222", "tpe": "PushEvent", "repo": {"name": "a"}}
    assert isinstance(Event.from_dict(a), Event)
    assert Event.from_dict(b) is None

