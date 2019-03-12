import logging
import re
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
        self.compiled_path = self._compile_path(path)
        self.method = method
        self.callback = callback

    def __call__(self, *args, **kwargs):
        return self.callback(*args, **kwargs)

    def __repr__(self):
        return '{} {}'.format(self.method or 'ALL', self.path)

    def match_path(self, path) -> bool:
        """
        Check whether path is matched.

        :param path:
        :return: bool
        """
        if self.compiled_path.match(path):
            return True
        return False

    def match_method(self, method) -> bool:
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

    def _compile_path(self, path):
        if '{' in path and '}' in path:
            sub_path = re.sub(r'{\w+?}', '[a-zA-Z0-9_-]+?', path)
            compiled_path = re.compile('^' + sub_path + '$')
        else:
            compiled_path = re.compile('^' + path + '$')
        return compiled_path


class Application:

    routers = []

    _request_middlewares = []

    _response_middlewares = []

    def __init__(self, conf=None):
        """

        :param BaseConfig conf: config object
        """
        if conf is None:
            conf = BaseConfig()
        self.config = conf
        self.stage_vars = {}
        logging.basicConfig(level=conf.LOG_LEVEL, format=conf.LOG_FORMATTER)
        if self.config.ENABLE_CORS:
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
            e1.log()
        except NotFoundError as e2:
            response = Response(e2, status=404)
        except MethodNotAllowedError as e3:
            response = Response(e3, status=405)
        except ServerError as e4:
            response = Response(e4, status=500)
            e4.log()
        except Exception as e:
            response = Response(e, status=500)
            logging.error(e)
        return response

    def run(self, event):
        """
        Run application.

        :param event:
        :return:
        """
        request = self.process_event(event)
        response = self.process(request)
        return response.parse_api_gateway()

    def register_router(self, path='/', method=None, callback=None):
        """
        Register router.

        :param path:
        :param method:
        :param callback: a function or dict of {'method': function}
        :return:
        """
        if isinstance(callback, dict):
            for m, func in callback.items():
                router = Router(path=path, method=m.upper(), callback=func)
                self.routers.append(router)
        else:
            router = Router(path=path, method=method, callback=callback)
            self.routers.append(router)
        return self.routers

    def find_router(self, path='/', method=None) -> Router:
        """
        Find router by path and method.

        :param path:
        :param method:
        :return: Router
        """
        find = list(filter(lambda r: r.match_path(path), self.routers))
        if find:
            for router in find:
                if router.match_method(method):
                    return router
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
            logging.warning('Invalid request middleware {}'.format(middleware))
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
            logging.warning('Invalid response middleware {}'.format(middleware))
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

    @staticmethod
    def preprocess_event(path='/', method='GET', body=None, query=None, path_parameters=None, headers=None, base64_encoded=False):
        """
        Preprocess event to build the standard event object.

        :param path:
        :param method:
        :param body:
        :param query:
        :param path_parameters:
        :param headers:
        :param base64_encoded:
        :return:
        """
        return {
            'path': path,
            'httpMethod': method,
            'base64_encoded': base64_encoded,
            'query': query,
            'headers': headers,
            'path_parameters': path_parameters,
            'body': body
        }
