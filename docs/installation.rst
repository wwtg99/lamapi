Installation
============

Python Version
--------------

We recommend using the latest version of Python 3. Lamapi supports Python 3.5 and newer.

Dependencies
------------

Lamapi is a serverless framework and depends on AWS Lambda and API Gateway, so we try to restrict dependent packages. This is the only package you need to try Lamapi except built-in packages.

Lamapi depends on AWS Lambda and API Gateway, you should deploy the code to AWS after development. We recommend you to use something like `Serverless Framework <https://serverless.com/>`_, check `here <https://serverless.com/framework/docs/providers/aws/guide/quick-start/>`_ to see how to use serverless framework on AWS.

Installation
------------

You should install lamapi in the current directory since you can upload it to Lambda.

.. code-block:: sh

  pip install -t lib lamapi


Lamapi is now installed. Check out the :doc:`/quickstart` or go to the
:doc:`Documentation Overview </index>`.

Check out our source from `Github <https://github.com/wwtg99/lamapi>`_.

Start Serverless Project using Serverless Framework and Lamapi
--------------------------------------------------------------

We assume you have **Serverless Framework** installed. `Installation Guide <https://serverless.com/framework/docs/providers/aws/guide/installation/>`_

Create A Project
****************

.. code-block:: sh

  serverless create --template aws-python3 --path hello


Update Configuration File
*************************

Update *serverless.yml* to something like this:

.. code-block:: yaml

  service: hello

  provider:
    name: aws
    runtime: python3.7

  functions:
    hello:
      handler: handler.handler
      events:
        - http:
            path: hello
            method: get


We use the python3.7 interpreter and add a function named *hello* listening at **/hello** path.


..

  Note, you should use lambda-proxy integration (it is the default value) for your function because it formats a standard request and response structure. See `Serverless Lambda Proxy Integration <https://serverless.com/framework/docs/providers/aws/events/apigateway/#lambda-proxy-integration>`_ and `AWS API Gateway Integration <https://docs.aws.amazon.com/apigateway/latest/developerguide/api-gateway-api-integration-types.html>`_.

Then we edit *handler.py* file as below:

.. code-block:: python

  from lib.lamapi import Application


  def handler(event, context):
      app = Application()

      @app.route(path='/hello', method='GET')
      def hello(request):
          return ['hello world']

      return app.run(event)


Deploy & Test Your Project
**************************

Deploy project

.. code-block:: sh

  serverless deploy


Invoke function

.. code-block:: sh

  serverless invoke -f hello -l


Next start to use **Lamapi** to build a web API :doc:`/quickstart`.
