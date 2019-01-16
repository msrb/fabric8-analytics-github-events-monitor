"""Monitor is an object that tracks activity in a Github repository."""

import logging
import json
import requests
import os
import random

from ghmonitor.models import Event, EventType

# for type hints:
from typing import List, Set, Union, Callable, Dict, Tuple

assert List
assert Set
assert Union
assert Callable
assert Dict
assert Tuple

logger = logging.getLogger('Monitor')
auth_header = None


def get_auth_header():
    # type: () -> Union[Dict[str, str], None]
    """
    Return dictionary for use with requests library.

    The dictionary contains authorization token for Github API.
    """
    token = random.choice(os.environ.get('GITHUB_TOKEN', '').split(','))
    if token:
        return {'Authorization': 'token ' + token}
    else:
        return None


def get_list_of_repos():
    # type: () -> List[str]
    """Read a list of repositories from the WATCH_REPOS environment variable."""
    repos = os.environ.get('WATCH_REPOS', '')
    return repos.split(' ')


def get_list_of_packages():
    # type: () -> List[str]
    """Read a list of Go packages from the WATCH_PACKAGES environment variable."""
    repos = os.environ.get('WATCH_PACKAGES', '')
    return repos.split(' ')


def github_request(url):
    # type: (str) -> Union[Tuple[int, Dict[str, str]], None]
    """
    Send a request to the Github API.

    Return a tuple with status code and message body as a dictionary or None in case of any failure.
    """
    try:
        r = requests.get(url, headers=auth_header)
        body = r.json()
        return r.status_code, body
    except requests.RequestException as e:
        logger.exception(e)
    except json.decoder.JSONDecodeError:
        logger.error('Response for URL={} does not contain JSON object.'.format(url))
    return None


def repository_exists(name):
    # type: (str) -> bool
    """
    Just check if the repository exists.

    Return false in case of any error (repo does not exist, communication failed etc.)
    """
    r = github_request('https://api.github.com/repos/' + name)
    if r is None:
        return False

    status_code, body = r
    message = body.get('message')
    if status_code == 200 and body.get('full_name') == name:
        logger.info('Successfully found {} repository'.format(name))
        return True
    elif message == 'Not Found':
        logger.error('Repository {} does not exist, check the configuration'.format(name))
    elif message is not None and "API rate limit exceeded" in message:
        logger.error('API rate limit exceeded')
    else:
        logger.error('Github response came in unexpected format (repo={})'.format(name))

    return False


class RepositoryMonitor:
    """Encapsulate Github repository and events, that has already been seen for it."""

    def __init__(self, package, repository):
        # type: (str, str) -> RepositoryMonitor
        """Create new monitor for given package and associated repository."""
        self.name = repository
        self.package = package
        self.seen_events = set()
        self.new_events = set()

    def get_new_events(self):
        # type: () -> Union[Set[Event], None]
        """Fetch new events from Github API and return them as a set."""
        r = github_request('https://api.github.com/repos/' + self.name + '/events')
        if r is None:
            logger.error('Failed to get new events for {} repository (communication error)'
                         .format(self.name))

        status_code, data = r
        if status_code == 200:
            return set(filter(lambda x: x is not None, map(lambda x: Event.from_dict(x), data)))
        else:
            logger.error('Failed to get new events for {} repository (status code != 200)'
                         .format(self.name))
            return None

    def _new_events_in_set(self, filtering_predicate, new_events):
        # type: (Callable[[Event], bool], Set[Event]) -> Set[Event]
        old = set(filter(filtering_predicate, self.seen_events))
        new = set(filter(filtering_predicate, new_events))
        return new - old

    def new_issues(self, events):
        # type: (Set[Event]) -> Set[Event]
        """Return a set of new issue events."""
        def p(x):
            return x.type == EventType.ISSUE

        return self._new_events_in_set(p, events)

    def new_commits(self, events):
        # type: (Set[Event]) -> Set[Event]
        """Return a set of new push events."""
        def p(x):
            return x.type == EventType.PUSH
        return self._new_events_in_set(p, events)

    def new_pull_requests(self, events):
        # type: (Set[Event]) -> Set[Event]
        """Return a set of new pull-request events."""
        def p(x):
            return x.type == EventType.PULL_REQUEST
        return self._new_events_in_set(p, events)

    def __str__(self):
        """Pretty print."""
        return '<{} for {} repository>'.format(self.__class__.__name__, self.name)
