"""Utility functions for the run.py script."""

from ghmonitor.backend import create_pr_notification, create_push_notification, \
    create_issue_notification
from ghmonitor.gopkg.translate import translate
from ghmonitor.monitor import repository_exists, get_list_of_packages
from ghmonitor.monitor import RepositoryMonitor

# For type hints:
from ghmonitor.backend import Backend
from typing import List

assert Backend
assert List


def create_monitors():
    # type: () -> List[RepositoryMonitor]
    """
    Create monitors for this service.

    Read Go package names from the environment, translate the names to Github repositories and
    create monitors that encapsulate them.
    :return: List of monitors
    """
    packages = get_list_of_packages()
    repos = list(filter(lambda y: y[1] is not None, map(lambda x: (x, translate(x)), packages)))
    repos = list(filter(lambda x: repository_exists(x[1]), repos))
    monitors = list(map(lambda x: RepositoryMonitor(*x), repos))

    return monitors


def process_new_events(monitor, backend):
    # type: (RepositoryMonitor, Backend) -> None
    """Try to fetch new events for the monitor, send notifications to the backend."""
    new_events = monitor.get_new_events()
    if new_events is None:
        return

    new_issues = monitor.new_issues(new_events)
    if new_issues != set():
        for issue in new_issues:
            backend.notify(create_issue_notification(monitor.package, monitor.name, issue.id))

    new_commits = monitor.new_commits(new_events)
    if new_commits != set():
        backend.notify(create_push_notification(monitor.package, monitor.name))

    new_prs = monitor.new_pull_requests(new_events)
    if new_prs != set():
        for pr in new_prs:
            backend.notify(create_pr_notification(monitor.package, monitor.name, pr.id))

    monitor.seen_events = new_events
