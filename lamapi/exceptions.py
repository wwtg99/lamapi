import traceback
import logging


class HttpError(Exception):

    def log(self):
        logging.error('<{}> {}'.format(self.__class__.__name__, traceback.format_exc()))


class RequestError(HttpError):
    pass


class ServerError(HttpError):
    pass


class NotFoundError(HttpError):
    pass


class MethodNotAllowedError(HttpError):
    pass
