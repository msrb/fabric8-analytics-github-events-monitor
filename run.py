import logging
import os

from time import sleep

from ghmonitor.monitor import get_auth_header, repository_exists, get_list_of_repos, \
    get_list_of_packages
from ghmonitor.monitor import RepositoryMonitor
from ghmonitor.gopkg.translate import translate
from ghmonitor.backend import LoggerBackend, create_pr_notification, create_issue_notification, \
    create_push_notification


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
    packages = get_list_of_packages()
    repos = list(filter(lambda y: y[1] is not None, map(lambda x: (x, translate(x)), packages)))
    repos = list(filter(lambda x: repository_exists(x[1]), repos))
    monitors = list(map(lambda x: RepositoryMonitor(*x), repos))
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

            new_issues = m.new_issues(new_events)
            if new_issues != set():
                for issue in new_issues:
                    backend.notify(create_pr_notification(m.package, m.name, issue.id))

            new_commits = m.new_commits(new_events)
            if new_commits != set():
                backend.notify(create_push_notification(m.package, m.name))

            new_prs = m.new_pull_requests(new_events)
            if new_prs != set():
                for pr in new_prs:
                    backend.notify(create_pr_notification(m.package, m.name, pr.id))

            m.seen_events = new_events
        sleep(SLEEP_PERIOD)
