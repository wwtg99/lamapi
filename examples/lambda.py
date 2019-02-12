from lamapi.app import Application
from lamapi.wrappers import Response
from lamapi.exceptions import RequestError


def test4(request):
    return 'test4'


def lambda_handler(event, context):
    app = Application()

    @app.route(path='/test1', method='GET')
    def test1(request):
        q = request.query.get('query')
        p = request.path_param.get('name')
        return 'aaaaa'

    @app.route(path='/test2', method=['GET', 'POST'])
    def test2(request):
        return Response({'message': 'test2'})

    @app.route(path='/test3', method='PUT')
    def test3(request):
        p = request.data.get('param')
        if not p:
            raise RequestError('invalid')
        return {'message': p}

    app.register_router(path='/test4', callback=test4)

    return app.run(event)
