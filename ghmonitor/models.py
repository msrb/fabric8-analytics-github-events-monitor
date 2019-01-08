"""Classes representing Github events and associated stuff."""

import logging

from enum import Enum

logger = logging.getLogger('Monitor')


class UnknownEvent(Exception):
    """Exception for unknown event strings."""

    pass


class EventType(Enum):
    """Represent event types that we are interested in (new pull requests, issues, or comments)."""

    PUSH = 1
    PULL_REQUEST = 2
    ISSUE = 3

    @staticmethod
    def from_str(input_string):
        # type: (str) -> EventType
        """Create an event type from the string or raise the UnknownEvent exception."""
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
        """Create new event."""
        self.id = None
        self.type = None
        self.repo = None

    def __str__(self):
        """Return pretty formatted string describing the Event object."""
        return "<Event id='{}', type='{}', repo='{}'>".format(self.id, self.type, self.repo)

    def __eq__(self, other):
        """Needed for operations in a set."""
        return (self.id, self.type, self.repo) == (other.id, other.type, other.repo)

    def __hash__(self):
        """See https://docs.python.org/3/reference/datamodel.html#object.__hash__ for more info."""
        return hash((self.id, self.type, self.repo))

    @staticmethod
    def from_dict(input_dict):
        """
        Filter the input dictionary and type check its members.

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
