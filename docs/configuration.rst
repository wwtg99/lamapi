Configuration
=============

Use your own configuration object
---------------------------------

**Lamapi** use a simple config object to store variables. You can get config object by *config* attribute of *request* object.

.. code-block:: python

  def hello(request):
      // get config object
      config = request.config
      // get config variables
      log_level = request.config.LOG_LEVEL


You can define your own variables by extending the base config class.

Add a **config.py** file,

.. code-block:: python

  from lib.lamapi.config import BaseConfig


  class Config(BaseConfig):

      VAR1 = 'value1'


Then you can start application by this config class,

.. code-block:: python

  from lib.lamapi import Application
  from config import Config


  def handler(event, context):
      config = Config()
      app = Application(config)

      @app.route(path='/', method='GET')
      def hello(request):
          // get config variable
          var1 = request.config.VAR1


Load configuration from environments
------------------------------------

Mostly you want to config your application by environments.

Change your **config.py** file,

.. code-block:: python

  import os
  from lib.lamapi.config import BaseConfig


  class Config(BaseConfig):

      VAR1 = os.environ.get('VALUE1') or 'default'


Built-in configuration

There are also some built-in configuration defined in the BaseConfig class. You can change them by using environments.

**LOG_LEVEL**

Define the logging level, values [``FATAL``, ``ERROR``, ``WARNING``, ``INFO``, ``DEBUG``], default ``ERROR``

**LOG_FORMATTER**

Define the logging formatter, default ``%(asctime)s [%(levelname)s] %(filename)s (%(lineno)d): %(message)s``

**ENABLE_CORS**

Enable CORS or not, values [``on``, ``off``], default ``off``

