Quick Start
===========

A Minimal Application
---------------------

We assume you install Lamapi under **lib** directory and start a serverless project using Serverless Framework. :doc:`/installation`.

A minimal Lamapi application looks something like this:

.. code-block:: python

  from lib.lamapi.app import Application

  def lambda_handler(event, context):
      app = Application()

      @app.route(path='/', method='GET')
      def hello(request):
          return 'Hello'

      return app.run(event)


So what did that code do?

1. First we import **Application** class, an instance of this class will help us to handle http event and return response.
2. Next in the **lambda_handler()** function (which is the entry point for the Lambda) we create an instance of this class.
3. Then we use the **route()** decorator to tell Lamapi what URL should trigger our function.
4. The function receives a request object and returns the message we want to display in the user’s browser.

Just save it as hello.py or something similar. Then deploy it to the AWS Lambda and API Gateway or deploy using **Serverless Framework** as below.

.. code-block:: sh

  serverless deploy


Then test it as:

.. code-block:: sh

  serverless invoke -f hello


Then you will get output as below:

.. code-block:: sh

  blalbal


Is it as simple as Flask?


Routing
-------

Routing is as simple as **Flask**. Use *app.route* descriptor to functions with path and/or methods.

Listening on path ``/`` with all methods,

.. code-block:: python

  def lambda_handler(event, context):
      app = Application()

      @app.route(path='/')
      def hello(request):
          return 'Hello'

      return app.run(event)


Listening on path ``/`` with ``GET`` method,

.. code-block:: python

  def lambda_handler(event, context):
      app = Application()

      @app.route(path='/', method='GET')
      def hello(request):
          return 'Hello'

      return app.run(event)


Use list to listen on more methods,

.. code-block:: python

  def lambda_handler(event, context):
      app = Application()

      @app.route(path='/', method=['GET', 'POST'])
      def hello(request):
          return 'Hello'

      return app.run(event)


Request
-------

Each function will receive a request instance as parameter. You can use this object to get anything you want.

A request body from API Gateway will look like this:

.. code-block:: json

  {
    "body": "",
    "resource": "/hello",
    "path": "/hello",
    "httpMethod": "GET",
    "isBase64Encoded": false,
    "queryStringParameters": null,
    "pathParameters": null,
    "stageVariables": null,
    "headers": {
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
      "Accept-Encoding": "gzip, deflate, sdch",
      "Accept-Language": "en-US,en;q=0.8",
      "Cache-Control": "max-age=0",
      "User-Agent": "Custom User Agent String"
    }
    "requestContext": {
      //......
    }
  }


**Lamapi** framework will store this object in *request* object. And you can get all you want by accessing request object's attributes.


Request Path
************

.. code-block:: python

  def hello(request):
      path = request.path


Request Method
**************

.. code-block:: python

  def hello(request):
      method = request.method


Query Parameters
****************

.. code-block:: python

  def hello(request):
      id = request.query.get('id')
      # if request url is /hello?id=1
      # then id = 1
      name = request.query.get('name') or 'default'
      # give some default value


Form Data
*********

To access form data (data transmitted in a *POST* or *PUT* request) you can use the data attributes.

.. code-block:: python

  def hello(request):
      name = request.data.get('name') or 'default'


Path Parameters
***************

If you define some path parameters in API Gateway, you can get them by *path_param*. If you define your path as */hello/{name}*, then requested as */hello/world*, you will get path parameters as *name=world*.

.. code-block:: python

  def hello(request):
      name = request.path_param.get('name') or 'default'


Request Header
**************

Headers will be stored in *header* attribute as a dict.

.. code-block:: python

  def hello(request):
      accept = request.header.get('Accept')


Response
--------

Anything you return to handler function will be translated to a JSON object which will be returned to client. You can return a string, dict, list or any object can be encoded to json.

.. code-block:: python

  def hello(request):
      return 'hello world'


If you want to return a custom http code such as *400* or custom headers, you can build response object by yourself.

.. code-block:: python

  from lib.lamapi.wrappers import Response


  def hello(request):
      return Response([], status=400, headers={'X-CUSTOM': 'xxx'})


Where to go next? Learn deep about :doc:`/configuration`.
