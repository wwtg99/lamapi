import os
import logging
from .config import BaseConfig
from .wrappers import Request, Response
from .exceptions import RequestError, ServerError, NotFoundError, MethodNotAllowedError
from .middlewares import RequestMiddleware, ResponseMiddleware


class Router:
    """
    Basic router object.
    """

    def __init__(self, path='/', method=None, callback=None):
        """

        :param path: request path
        :param method: http method, GET, POST, PUT, DELETE or list of these methods, None for all.
        :param callback:
        """
        self.path = path
        self.method = method
        self.callback = callback

    def __call__(self, *args, **kwargs):
        return self.callback(*args, **kwargs)

    def __repr__(self):
        return '{} {}'.format(self.method or 'ALL', self.path)

    def match_method(self, method):
        """
        Check whether method is allowed.

        :param method:
        :return: bool
        """
        if method is None:
            method = 'GET'
        if self.method is None:
            return True
        if isinstance(self.method, list):
            for m in self.method:
                if m.upper() == method.upper():
                    return True
            return False
        elif isinstance(self.method, str):
            return self.method.upper() == method
        else:
            return False


class Application:

    routers = {}

    _request_middlewares = []

    _response_middlewares = []

    def __init__(self, environ=None, conf=None):
        if environ is None:
            environ = dict(os.environ)
        self.environ = environ
        if conf is None:
            conf = BaseConfig()
        self.config = conf
        self.stage_vars = {}
        logging.basicConfig(level=conf.log_level, format=conf.log_formatter)
        if self.config.enable_cors:
            from .middlewares import CorsMiddleware
            self.add_response_middleware(CorsMiddleware())

    def process_event(self, event) -> Request:
        """
        Process api http event to Request.

        :param event:
        :return: Request
        """
        data = {
            'path': event['path'],
            'method': event['httpMethod'],
            'base64_encoded': event['isBase64Encoded'] or False,
            'query': event['queryStringParameters'] or {},
            'headers': event['headers'] or {},
            'path_parameters': event['pathParameters'] or {},
            'body': event['body'] or ''
        }
        if 'stageVariables' in event and event['stageVariables']:
            self.stage_vars = event['stageVariables']
        return Request(environ=data, context=self)

    def process(self, request: Request) -> Response:
        """
        Process request to response.

        :param Request request:
        :return: Response
        """
        try:
            # process request middlewares
            for m in self._request_middlewares:
                request = m.handle(request)
                if request is None:
                    raise ServerError('Fail to process request middleware {}'.format(m))
            # process router
            router = self.find_router(path=request.path, method=request.method)
            response = router(request=request)
            if not isinstance(response, Response):
                response = Response(response)
            # process response middlewares
            for m in self._response_middlewares:
                response = m.handle(response)
                if response is None:
                    raise ServerError('Fail to process response middleware {}'.format(m))
        except RequestError as e1:
            response = Response(e1, status=400)
        except NotFoundError as e2:
            response = Response(e2, status=404)
        except MethodNotAllowedError as e3:
            response = Response(e3, status=405)
        except ServerError as e4:
            response = Response(e4, status=500)
        except Exception as e:
            response = Response(e, status=500)
        return response

    def run(self, event):
        request = self.process_event(event)
        response = self.process(request)
        return response.parse_api_gateway()

    def register_router(self, path='/', method=None, callback=None):
        """
        Register router.

        :param path:
        :param method:
        :param callback:
        :return:
        """
        router = Router(path=path, method=method, callback=callback)
        if path in self.routers:
            self.routers[path].append(router)
        else:
            self.routers[path] = [router]
        return self.routers

    def find_router(self, path='/', method=None) -> Router:
        """
        Find router by path and method.

        :param path:
        :param method:
        :return: Router
        """
        if path in self.routers:
            for r in self.routers[path]:
                if isinstance(r, Router) and r.match_method(method):
                    return r
            raise MethodNotAllowedError('Method not allowed')
        else:
            raise NotFoundError('Not Found')

    def add_request_middleware(self, middleware):
        """
        Add request middleware.

        :param middleware:
        :return:
        """
        if isinstance(middleware, RequestMiddleware):
            self._request_middlewares.append(middleware)
        else:
            logging.warning('invalid request middleware {}'.format(middleware))
        return self

    def add_response_middleware(self, middleware):
        """
        Add response middleware.

        :param middleware:
        :return:
        """
        if isinstance(middleware, ResponseMiddleware):
            self._response_middlewares.append(middleware)
        else:
            logging.warning('invalid response middleware {}'.format(middleware))
        return self

    def route(self, path='/', method=None):
        """
        Decorator for router.

        :param path:
        :param method:
        :return:
        """
        def wrapper(func):
            self.register_router(path=path, method=method, callback=func)
            return func
        return wrapper
