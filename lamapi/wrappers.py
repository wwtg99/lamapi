import json
import base64
from .utils import cached_property


class Request:
    """
    Basic request object.
    """

    def __init__(self, environ, context=None):
        self.environ = environ
        self.context = context

    @cached_property
    def path(self) -> str:
        """
        Get requested path.

        :return: str
        """
        return self.environ.get('path') or '/'

    @cached_property
    def resource(self) -> str:
        """
        Get requested resource.

        :return: str
        """
        return self.environ.get('resource') or self.path

    @cached_property
    def method(self) -> str:
        """
        Get requested method.

        :return: str
        """
        m = self.environ['method'] or 'GET'
        return m.upper()

    @cached_property
    def query(self) -> dict:
        """
        Get query parameters.

        :return: dict
        """
        return self.environ['query'] or {}

    @cached_property
    def header(self) -> dict:
        """
        Get requested headers.

        :return: dict
        """
        return self.environ['headers'] or {}

    @cached_property
    def data(self) -> dict:
        """
        Get requested body.

        :return: dict
        """
        base64_encoded = self.environ['base64_encoded'] or False
        return self.get_data(base64_encoded) or {}

    def get_data(self, base64_encoded=False) -> dict:
        """
        Get requested body as dict and also check if is base64 encoded.

        :param base64_encoded:
        :return: dict
        """
        body = self.raw_body
        if base64_encoded:
            body = base64.b64decode(body)
        try:
            return json.loads(body)
        except Exception as e:
            return {}

    @property
    def raw_body(self):
        """
        Get raw requested body.

        :return: dict
        """
        return self.environ['body']

    @cached_property
    def path_param(self) -> dict:
        return self.environ['path_parameters'] or {}

    @property
    def config(self):
        if self.context:
            return self.context.config
        else:
            return None


class Response:
    """
    Basic response object.
    """

    charset = 'utf-8'

    default_content_type = 'application/json'

    default_status = 200

    base64_encoded = False

    def __init__(self, response=None, status=None, headers=None):
        self.status_code = status if status is not None and isinstance(status, int) else self.default_status
        self.headers = headers if headers is not None and isinstance(headers, dict) else {}
        if 'content-type' not in self.headers:
            self.headers['content-type'] = self.default_content_type
        self.response = response or []

    def __repr__(self):
        return '<{} [{}]>'.format(self.__class__.__name__, self.status_code)

    def parse_body(self):
        if isinstance(self.response, (dict, list, tuple, set)):
            return json.dumps(self.response, default=lambda x: str(x))
        elif isinstance(self.response, Exception):
            return json.dumps({'message': str(self.response)})
        else:
            return str(self.response)

    def parse_api_gateway(self) -> dict:
        """
        Parse response to API Gateway.

        :return: dict
        """
        d = {
            "statusCode": self.status_code,
            "body": self.parse_body(),
            "headers": self.headers,
            "isBase64Encoded": self.base64_encoded
        }
        return d
