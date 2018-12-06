import logging
import json
import os

from models import Event

logger = logging.getLogger('Monitor')

if __name__ == "__main__":
    LOGLEVEL = os.environ.get('LOGLEVEL', 'WARNING').upper()
    logging.basicConfig(level=LOGLEVEL)
    logger.info("Starting the monitor service")
    with open('events.json') as f:
        data = json.load(f)
        events = list(filter(lambda x: x is not None, map(lambda x: Event.from_dict(x), data)))
        for e in events:
            print(e.id, e.repo, e.type)
