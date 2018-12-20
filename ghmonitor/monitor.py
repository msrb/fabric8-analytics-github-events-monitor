import logging
import json
import requests
import os

from models import Event, EventType
from time import sleep

logger = logging.getLogger('Monitor')
auth_header = None


def get_auth_header():
    token = os.environ.get('GITHUB_TOKEN')
    if token is not None:
        return {'Authorization': 'token ' + token}
    else:
        return None


def get_list_of_repos():
    repos = os.environ.get('WATCH_REPOS', '')
    return repos.split(' ')


def github_request(url):
    try:
        r = requests.get(url, headers=auth_header)
        body = r.json()
        return r.status_code, body
    except requests.RequestException as e:
        logger.exception(e)
    except json.decoder.JSONDecodeError:
        logger.error('Response for URL={} does not contain JSON object.'.format(url))
    return None


def repository_exists(name: str) -> bool:
    """
    Just check if the repository exists. Return false in case of any error (repo does not exist,
    communication failed etc.)
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
    def __init__(self, name):
        self.name = name
        self.seen_events = set()
        self.new_events = set()

    def get_new_events(self):
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
        old = set(filter(filtering_predicate, self.seen_events))
        new = set(filter(filtering_predicate, new_events))
        return len(new - old) > 0

    def new_issues(self, events):
        p = lambda x: x.type == EventType.ISSUE
        return self._new_events_in_set(p, events)

    def new_commits(self, events):
        p = lambda x: x.type == EventType.PUSH
        return self._new_events_in_set(p, events)

    def new_pull_requests(self, events):
        p = lambda x: x.type == EventType.PULL_REQUEST
        return self._new_events_in_set(p, events)

    def __str__(self):
        return '<{} for {} repository>'.format(self.__class__.__name__, self.name)


if __name__ == "__main__":
    # Set up logging
    LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
    logging.basicConfig(level=LOGLEVEL)
    logger.info("Starting the monitor service")

    # In seconds
    SLEEP_PERIOD = float(os.environ.get('SLEEP_PERIOD', 30))

    # Set up list of repositories
    auth_header = get_auth_header()
    repos = list(filter(repository_exists, get_list_of_repos()))
    monitors = list(map(lambda x: RepositoryMonitor(x), repos))
    logger.info('Monitoring these repositories:')
    for m in monitors:
        logger.info(str(m))

    while True:
        # Run the monitor forever
        for m in monitors:
            new_events = m.get_new_events()
            if m.new_issues(new_events):
                logger.info('There are new issues for ' + m.name)
            if m.new_commits(new_events):
                logger.info('There are new commits for ' + m.name)
            if m.new_pull_requests(new_events):
                logger.info('There are new pull requests for ' + m.name)
            m.seen_events = new_events
        sleep(SLEEP_PERIOD)


def test_repo_exists():
    """
    Check the function using some well known repo, be careful though. This test
    may fail without Internet connection, rate limiting etc.
    """
    assert repository_exists('rust-lang/rust')
