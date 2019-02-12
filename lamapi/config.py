

class BaseConfig:
    """
    Basic class for config.
    """

    # logger configuration
    log_level = 'ERROR'
    log_formatter = '%(asctime)s [%(levelname)s] %(filename)s (%(lineno)d): %(message)s'

    # cors
    enable_cors = False
