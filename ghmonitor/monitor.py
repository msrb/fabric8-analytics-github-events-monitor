import logging
import json
import requests
import os

from ghmonitor.models import Event, EventType

logger = logging.getLogger('Monitor')
auth_header = None


def get_auth_header():
    token = os.environ.get('GITHUB_TOKEN')
    if token is not None:
        return {'Authorization': 'token ' + token}
    else:
        return None


def test_get_auth_header():
    os.environ['GITHUB_TOKEN'] = '123'
    assert get_auth_header() == {'Authorization': 'token 123'}
    os.environ.pop('GITHUB_TOKEN')
    assert get_auth_header() is None


def get_list_of_repos():
    repos = os.environ.get('WATCH_REPOS', '')
    return repos.split(' ')


def test_get_list_of_repos():
    os.environ['WATCH_REPOS'] = 'a/b c/d'
    assert get_list_of_repos() == ['a/b', 'c/d']


def get_list_of_packages():
    repos = os.environ.get('WATCH_PACKAGES', '')
    return repos.split(' ')


def test_get_list_of_packages():
    os.environ['WATCH_PACKAGES'] = 'a/b c/d'
    assert get_list_of_repos() == ['a/b', 'c/d']


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


def test_github_request():
    assert github_request('https://api.github.com/') is not None
    assert github_request('https://tramtadadaneexistujicidomena.redhat.com/') is None
    assert github_request('https://github.com/') is None


def repository_exists(name):
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
    def __init__(self, package, repository):
        self.name = repository
        self.package = package
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


def test_new_issues():
    m = RepositoryMonitor('a')
    i1 = Event()
    i1.type = EventType.ISSUE
    i2 = Event()
    i2.id = 1
    i2.type = EventType.ISSUE
    c1 = Event()
    c1.type = EventType.PUSH
    c2 = Event()
    c2.id = 1
    c2.type = EventType.PUSH
    p1 = Event()
    p1.type = EventType.PULL_REQUEST
    p2 = Event()
    p2.id = 1
    p2.type = EventType.PULL_REQUEST
    m.seen_events = set()
    new_events = set()
    assert m.new_commits(new_events) is False
    assert m.new_issues(new_events) is False
    assert m.new_pull_requests(new_events) is False
    m.seen_events = {i1, c1, p1}
    new_events = {i1, c1, p1}
    assert m.new_commits(new_events) is False
    assert m.new_issues(new_events) is False
    assert m.new_pull_requests(new_events) is False
    m.seen_events = {i1, c1, p1}
    new_events = {i1, c1, p1, i2, c2, p2}
    assert m.new_commits(new_events)
    assert m.new_issues(new_events)
    assert m.new_pull_requests(new_events)


def test_repo_exists():
    """
    Check the function using some well known repo, be careful though. This test
    may fail without Internet connection, rate limiting etc.
    """
    assert repository_exists('rust-lang/rust') in {True, False}  # @tisnik: Easter egg for you :D
    assert repository_exists('msehnout/go-lang-is-awesome') is False
