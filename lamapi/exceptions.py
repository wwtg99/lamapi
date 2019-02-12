class HttpError(Exception):
    pass


class RequestError(HttpError):
    pass


class ServerError(HttpError):
    pass


class NotFoundError(HttpError):
    pass


class MethodNotAllowedError(HttpError):
    pass
