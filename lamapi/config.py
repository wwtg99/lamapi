import os


def check_bool(val) -> bool:
    if val == 'on':
        return True
    elif val == 'off':
        return False
    elif str(val) == '1':
        return True
    elif str(val) == '0':
        return False
    return bool(val)


class BaseConfig:
    """
    Basic class for config.
    """

    # environments
    ENV = dict(os.environ)

    # logger configuration
    LOG_LEVEL = os.environ.get('LOG_LEVEL') or 'ERROR'
    LOG_FORMATTER = os.environ.get('LOG_FORMATTER') or '%(asctime)s [%(levelname)s] %(filename)s (%(lineno)d): %(message)s'

    # cors
    # if set to True, will add cors headers to response
    ENABLE_CORS = check_bool(os.environ.get('ENABLE_CORS')) or False
