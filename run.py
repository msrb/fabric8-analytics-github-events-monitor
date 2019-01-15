"""Entry point for the service."""

import logging
import os

from time import sleep

from ghmonitor.monitor import get_auth_header
from ghmonitor.backend import get_backend_by_name
from ghmonitor.utils import create_monitors, process_new_events


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
    monitors = create_monitors()
    logger.info('Monitoring these repositories:')
    for m in monitors:
        logger.info(str(m))

    # Set up backend for notifications
    backend = get_backend_by_name(os.environ.get('BACKEND_CLASS', 'LoggerBackend'))

    while True:
        # Run the monitor forever
        for m in monitors:
            process_new_events(m, backend)

        sleep(SLEEP_PERIOD)
