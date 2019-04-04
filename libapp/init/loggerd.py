__author__ = 'rahul'

import logging
import os
from logging.handlers import TimedRotatingFileHandler

from libapp.config import libconf


def init_app(app):

    if not os.path.exists(libconf.LOG_FILE_PATH):
        os.makedirs(libconf.LOG_FILE_PATH)

    logfile = os.path.join(libconf.LOG_FILE_PATH, libconf.LOG_FILE_NAME.format(log=app.import_name))
    formatter = logging.Formatter(libconf.LOG_FORMATTER)

    handler = TimedRotatingFileHandler(logfile, when=libconf.LOG_ROTATION_WHEN, backupCount=libconf.LOG_BACKUP_COUNT,
                                       utc=libconf.LOG_UTC_STATUS)
    handler.setLevel(logging.WARNING)
    handler.setFormatter(formatter)

    # werkzeug log messages
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.WARNING)
    log.addHandler(handler)

    app.logger.addHandler(handler)
