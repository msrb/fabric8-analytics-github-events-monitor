import logging
import os
from time import sleep


from ghmonitor.monitor import get_auth_header, repository_exists, get_list_of_repos
from ghmonitor.monitor import RepositoryMonitor
from ghmonitor.backend import LoggerBackend


logger = logging.getLogger('Monitor')


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

    # Set up backend for notifications
    # TODO: use selinon instead of the logger
    backend = LoggerBackend()

    while True:
        # Run the monitor forever
        for m in monitors:
            new_events = m.get_new_events()
            if new_events is None:
                continue

            if m.new_issues(new_events):
                backend.notify('There are new issues for ' + m.name)
            if m.new_commits(new_events):
                backend.notify('There are new commits for ' + m.name)
            if m.new_pull_requests(new_events):
                backend.notify('There are new pull requests for ' + m.name)
            m.seen_events = new_events
        sleep(SLEEP_PERIOD)
