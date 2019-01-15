"""All classes inherited from the Backend can be used for sending notifications."""

import logging
import json

from abc import ABC, abstractmethod
from selinon import run_flow
from f8a_worker.setup_celery import init_celery, init_selinon

logger = logging.getLogger('Monitor')


class InvalidBackendClass(Exception):
    """Exception for invalid backend class name."""


def get_backend_by_name(cls_str):
    # type: (str) -> ghmonitor.Backend
    """
    Instantiate and return backend object.

    :param cls_str: str, backend class name
    :return: instance of the selected backend class
    :raise: InvalidBackendClass if backend class doesn't exist
    """
    try:
        return globals()[cls_str]()
    except KeyError:
        raise InvalidBackendClass('Invalid backend class name: {cls}'.format(cls=cls_str))


class Backend(ABC):
    """
    Backend for sending notifications.

    An abstract class, that defines interface for any backend implementation. The backend is
    used for sending notifications regarding new events in the repositories, that we monitor.
    """

    @abstractmethod
    def notify(self, notification_string):
        # type: (str) -> None
        """Send notification."""
        pass


class LoggerBackend(Backend):
    """
    Simple backend, that will use the logger for sending notifications.

    Useful mainly for local development and testing.
    """

    def __init__(self):
        """Create this backend."""
        logger.info('Using logger backend')

    def notify(self, notification_string):
        """See parent class."""
        logger.info(notification_string)


SELINON_FLOW_NAME = 'golangCVEPredictionsFlow'


class SelinonBackend(Backend):
    """Production backend that is connected to Selinon(Celery(SQS@AWS))."""

    def __init__(self):
        """Create this backend."""
        super().__init__()
        init_celery(result_backend=False)
        init_selinon()

    def notify(self, notification_string):
        """See parent class."""
        run_flow(SELINON_FLOW_NAME, json.loads(notification_string))


def create_pr_notification(package, repository, id):
    # type: (str, str, int) -> str
    """Create notification about new PR encoded into JSON string."""
    notification_dict = {
        "repository": repository,
        "package": package,
        "event": "pull-request",
        "id": id
    }
    return json.dumps(notification_dict)


def create_issue_notification(package, repository, id):
    # type: (str, str, int) -> str
    """Create notification about new issue encoded into JSON string."""
    notification_dict = {
        "repository": repository,
        "package": package,
        "event": "issue",
        "id": id
    }
    return json.dumps(notification_dict)


def create_push_notification(package, repository):
    # type: (str, str) -> str
    """Create notification about new push event encoded into JSON string."""
    notification_dict = {
        "repository": repository,
        "package": package,
        "event": "push",
    }
    return json.dumps(notification_dict)
