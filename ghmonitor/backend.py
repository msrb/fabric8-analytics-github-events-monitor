import logging

from abc import ABC, abstractmethod
from selinon import run_flow
from f8a_worker.setup_celery import init_celery

logger = logging.getLogger('Monitor')


class Backend(ABC):

    @abstractmethod
    def notify(self, notification_string):
        pass


class LoggerBackend(Backend):

    def __init__(self):
        logger.info('Using logger backend')

    def notify(self, notification_string):
        logger.info(notification_string)


SELINON_FLOW_NAME = 'golangCVEPredictionsFlow'


class SelinonBackend(Backend):

    def __init__(self):
        pass

    def notify(self, notification_string):
        init_celery(result_backend=False)
        run_flow(SELINON_FLOW_NAME, notification_string)
