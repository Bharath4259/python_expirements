import logging
import sys


class Logger:

    APP_LOGGER_NAME = 'CustomLogger'

    def __init__(self, app_name=None) -> None:
        self.APP_LOGGER_NAME = (app_name or self.APP_LOGGER_NAME)

    def create_applevel_logger(self, is_debug=True, file_name=None):

        logger = logging.getLogger(self.APP_LOGGER_NAME)
        logger.setLevel(logging.DEBUG if is_debug else logging.INFO)

        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        sh = logging.StreamHandler(sys.stdout)
        sh.setFormatter(formatter)
        logger.handlers.clear()
        logger.addHandler(sh)

        if file_name:
            fh = logging.FileHandler(file_name)
            fh.setFormatter(formatter)
            logger.addHandler(fh)

        return logger


    def get_logger(self, module_name):
        return logging.getLogger(self.APP_LOGGER_NAME).getChild(module_name)
