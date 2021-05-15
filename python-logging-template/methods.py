import utils

log = utils.app_log.get_logger(__name__)


def method_1(param1, param2):
    log.debug("Executing method_1 function.")
    return param1 * param2
