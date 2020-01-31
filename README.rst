.. WRP Client documentation master file, created by
   sphinx-quickstart on Tue Jan 28 10:36:49 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

WRP Client - Workswell Remote Protocol Client
=============================================

Welcome to the WRP Client's documentation! WRP Client and `WRP Server <https://github.com/Kasape/wrp-server/>`_ are two parts of a driver that allows to connect to the `Workswell InfraRed Camera <https://www.workswell-thermal-camera.com/workswell-infrared-camera-wic/>`_ using Python. This repository contains the client part, that is written in Python. The second part, `WRP Server <https://github.com/Kasape/wrp-server/>`_, is written in C# because the Workswell company provides and supports access to the cameras only through their C# SDK and not throught any other language. 

Installation
----------------------

The simplest way to install WRP client is from the pypi:

.. code-block:: bash

  pip install wrpclient

Alternative method is to build this repository:

.. code-block:: bash

  git clone https://github.com/Kasape/wrpclient.git
  cd wrpclient
  python setup.py install

Usage
----------------------

This project is implemented using asyncio library. But because using asyncio library can be a little problematic for beginners in Python, there are also synchronous wrappers about the asynchronous ones. First we have to create a instance of Client class and then connect it to the server: 

.. code-block:: python

	from datetime import datetime
	import wrp_client
	import asyncio

	client = wrp_client.Client()
	SERVER_IP_ADDRESS = "127.0.0.1"
	# synchronous wrapper for the method (coroutine) 
	# client.connect_async(ip_adress=SERVER_IP_ADDRESS)
	client.connect(ip_adress=SERVER_IP_ADDRESS, timeout="20")

Once the client is connected to the server, we can get list of all cameras that was identified by the server.  

.. code-block:: python

	# get all cameras
	all_cameras = client.get_cameras(timeout="20")

Or we can get only one camera identified by the serial number. If the camera is not available, ValueError exception is raised. 
Then we have to open the camera to get frame(s):

.. code-block:: python

	# find camera with specific serial number
	my_camera = client.get_camera(serial_number="ABCDEF", timeout="20")

	my_camera.open(timeout="20")

	# Return 2D frame (numpy matrix) with dtype np.float32 filled with raw data (decimal values of temperatures)
	frame = my_camera.get_frame(timeout="20")

As you can see, all the functions above have parameter timeout. That is because each function is sending some request and is expecting response from to the server and latence of the server depends on the latence of the cameras. There are also asynchronous versions of these functions for more advanced users. They are named `xxx_async` as shown in case of `client.connect_async`.

You can also ask camera for the continuous stream of frames:

.. code-block:: python

	def callback(frame):
		time_str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
		frame_color = cv2.applyColorMap(frame, cv2.COLORMAP_JET)
		cv2.imwrite(f"frame-{time_str}.jpg", frame_color)

	# give handler for continuous shot that saves colorized images with timestamp suffix
	my_camera.start_continuous_shot(callback)

	# wait some time to collect images
	asyncio.sleep(5)

	my_camera.stop_continuous_shot(callback)

If you want to use the API in IPython enviroment (most common are Jupyter notebooks), you have to install `Nest asyncio <https://pypi.org/project/nest-asyncio/>`_ and run the following code before using wrpclient:

.. code-block:: python

	import nest_asyncio
	nest_asyncio.apply()



Documentation
-------------
Above you can find guide for installation and example of usage. The full version of the documentation also containing class and methods description (API) can be found on `ReadTheDocs page <https://wrpclient.readthedocs.io/>`_ or you can build it from a repository with code: 

.. code-block:: bash

  git clone https://github.com/Kasape/wrpclient.git
  cd wrpclient/docs
  pip install sphinx
  make html

and open it with your browser on the address ``file://<path_to_repo>/docs/_build/html/index.html``.

Licence
-------
This project has GNU GPLv3 License.
