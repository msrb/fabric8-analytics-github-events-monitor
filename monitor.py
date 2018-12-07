import logging
import json
import os

import requests

from models import Event

logger = logging.getLogger('Monitor')


def get_list_of_repos():
    repos = os.environ.get('WATCH_REPOS', '')
    return repos.split(' ')


def repository_exists(name: str) -> bool:
    try:
        r = requests.get('https://api.github.com/repos/' + name)
        if r.status_code == 200:
            body = r.json()
            if body.get('full_name') == name:
                logger.info('Successfully found {} repository'.format(name))
                return True
            elif body.get('message') == 'Not Found':
                logger.error('Repository {} does not exist, check the configuration'.format(name))
                return False
            else:
                logger.error('Github response came in unexpected format (repo={})'.format(name))
    except requests.RequestException as e:
        logger.exception(e)
    except json.decoder.JSONDecodeError:
        logger.error('Failed to verify existence of {} repository, response body does not contain'
                     'JSON object.'.format(name))
    return False


if __name__ == "__main__":
    # Set up logging
    LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
    logging.basicConfig(level=LOGLEVEL)
    logger.info("Starting the monitor service")

    # Set up list of repositories
    repos = list(filter(repository_exists, get_list_of_repos()))
    print(repos)

    with open('events.json') as f:
        data = json.load(f)
        events = list(filter(lambda x: x is not None, map(lambda x: Event.from_dict(x), data)))
        for e in events:
            print(e.id, e.repo, e.type)


def test_repo_exists():
    assert repository_exists('rust-lang/rust')
