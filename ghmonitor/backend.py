import logging
import json

from abc import ABC, abstractmethod
from selinon import run_flow
from f8a_worker.setup_celery import init_celery

logger = logging.getLogger('Monitor')


class Backend(ABC):
    """
    An abstract class, that defines interface for any backend implementation. The backend is
    used for sending notifications regarding new events in the repositories, that we monitor.
    """

    @abstractmethod
    def notify(self, notification_string):
        # type: (str) -> None
        pass


class LoggerBackend(Backend):
    """
    Simple backend, that will use the logger for sending notifications. Useful mainly for
    local development and testing.
    """

    def __init__(self):
        logger.info('Using logger backend')

    def notify(self, notification_string):
        logger.info(notification_string)


SELINON_FLOW_NAME = 'golangCVEPredictionsFlow'


class SelinonBackend(Backend):
    """
    Production backend that is connected to Selinon(Celery(SQS@AWS))
    """

    def __init__(self):
        pass

    def notify(self, notification_string):
        init_celery(result_backend=False)
        run_flow(SELINON_FLOW_NAME, notification_string)


def create_pr_notification(package, repository, id):
    # type: (str, str, int) -> str
    notification_dict = {
        "repository": repository,
        "package": package,
        "event": "pull-request",
        "id": id
    }
    return json.dumps(notification_dict)


def create_issue_notification(package, repository, id):
    # type: (str, str, int) -> str
    notification_dict = {
        "repository": repository,
        "package": package,
        "event": "issue",
        "id": id
    }
    return json.dumps(notification_dict)


def create_push_notification(package, repository):
    # type: (str, str) -> str
    notification_dict = {
        "repository": repository,
        "package": package,
        "event": "push",
    }
    return json.dumps(notification_dict)
