import logging
import logging.handlers
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.StreamHandler(sys.stdout)
logformat = logging.Formatter('slackbot: [%(name)s] %(message)s')
handler.setFormatter(logformat)
logger.addHandler(handler)
