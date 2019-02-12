

class BaseMiddleware:

    def __repr__(self):
        return self.__class__.__name__


class RequestMiddleware(BaseMiddleware):

    def handle(self, request):
        return request


class ResponseMiddleware(BaseMiddleware):

    def handle(self, response):
        return response


class CorsMiddleware(ResponseMiddleware):

    CORS_HEADERS = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET,POST,PUT,OPTIONS,DELETE',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'
    }

    def handle(self, response):
        if response.status_code < 400:
            response.headers.update(self.CORS_HEADERS)
        return response
