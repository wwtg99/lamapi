import json
import pytest
from lamapi.app import Application, Router
from lamapi.exceptions import NotFoundError, MethodNotAllowedError


class TestApplication:

    def test_router(self):
        router = Router(path='/test1', method='GET', callback=str)
        assert router.path == '/test1'
        assert router.method == 'GET'
        assert router.match_method('GET') is True
        assert router.match_method('POST') is False
        assert router.match_method('PUT') is False
        assert router.match_method('DELETE') is False
        router = Router(path='/test1', method=['GET', 'POST'])
        assert router.match_method('GET') is True
        assert router.match_method('POST') is True
        assert router.match_method('PUT') is False
        assert router.match_method('DELETE') is False
        router = Router(path='/test1')
        assert router.match_method('GET') is True
        assert router.match_method('POST') is True
        assert router.match_method('PUT') is True
        assert router.match_method('DELETE') is True
        assert router.match_path('/test1') is True
        assert router.match_path('/test1/') is False
        assert router.match_path('/test2') is False
        router = Router(path='/test2/{id}')
        assert router.match_path('/test2/1') is True
        assert router.match_path('/test2/aa') is True
        assert router.match_path('/test2/b1') is True
        assert router.match_path('/test2/c2_aa') is True
        assert router.match_path('/test2') is False
        assert router.match_path('/test2/') is False
        assert router.match_path('/test2/1/') is False
        assert router.match_path('/test2/a-1') is True
        assert router.match_path('/test2/a_1') is True
        assert router.match_path('/test2/a=1') is False

    def test_register_router(self):
        app = Application()
        app.register_router('/t1', 'GET', str)
        app.register_router('/t1', 'POST', str)
        app.register_router('/t2', ['GET', 'POST'], str)
        app.register_router('/t3', callback=str)
        assert app.find_router('/t1', 'GET') is not None
        assert app.find_router('/t1') is not None
        assert app.find_router('/t1', 'POST') is not None
        with pytest.raises(MethodNotAllowedError):
            assert app.find_router('/t1', 'PUT')
        with pytest.raises(MethodNotAllowedError):
            assert app.find_router('/t1', 'DELETE')
        assert app.find_router('/t2', 'GET') is not None
        assert app.find_router('/t2', 'POST') is not None
        with pytest.raises(MethodNotAllowedError):
            assert app.find_router('/t2', 'PUT')
        with pytest.raises(MethodNotAllowedError):
            assert app.find_router('/t2', 'DELETE')
        assert app.find_router('/t3', 'GET') is not None
        assert app.find_router('/t3', 'POST') is not None
        assert app.find_router('/t3', 'PUT') is not None
        assert app.find_router('/t3', 'DELETE') is not None
        with pytest.raises(NotFoundError):
            assert app.find_router('/t4', 'GET') is not None

    def test_application(self):
        app = Application()
        event = {
            'path': '/test',
            'httpMethod': 'GET',
            'isBase64Encoded': False,
            'queryStringParameters': {'name': 'name1'},
            'headers': {'Host': '12345.com'},
            'pathParameters': {'id': 'id1'},
            'body': '{"type": "int"}'
        }
        request = app.process_event(event)
        assert request.path == event['path']
        assert request.method == event['httpMethod']
        assert request.query == event['queryStringParameters']
        assert request.path_param == event['pathParameters']
        assert request.header == event['headers']
        assert request.data == json.loads(event['body'])

        def test1(request):
            return 'aaa'

        app.register_router(path='/test', method='GET', callback=test1)
        res = app.process(request)
        assert res.status_code == 200
        assert res.response == 'aaa'
