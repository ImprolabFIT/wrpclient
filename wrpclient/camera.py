class Camera:
    '''
    Represents camera with corresponding hardware on the server-side of application.
    Can be used to get frame or start continuous shot.
    Instances of this class should not be created by the user directly (camera = Camera()) but they should be obtained using client.get_cameras().
    '''

    DEFAULT_TIMEOUT = 10
    # Keys are names in C# SDK, values are names of the attributes in Python
    ATTRIBUTES = {
        'SerialNumber': ('serial_number', str),
        'ModelName': ('model_name', str),
        'Width': ('width', int),
        'Height': ('height', int),
        'CameraMaxFPS': ('camera_max_fps', float),
        'Version': ('version', str),
        'ManufacturerInfo': ('manufacturer_info', str),
        'VendorName': ('vendor_name', str)
    }

    def __init__(self, connector):
        self.__connector = connector

    def __repr__(self):
        res = "Camera:"
        for key, (attr_name, attr_dtype) in Camera.ATTRIBUTES.items():
            if(attr_dtype == str):
                default_value = "N/A"
            elif(attr_dtype in [float, int]):
                default_value = 0
            else:
                default_value = None
            res += f"\n\t{attr_name}=" + \
                str(getattr(self, attr_name, default_value))
        return res + "\n"

    def open(self, timeout=DEFAULT_TIMEOUT):
        '''

        Connect to the camera throught the server.
        `ValueError exception <https://docs.python.org/3/library/exceptions.html#ValueError>`_  is raised when another camera is already open.


        **Params**

        * timeout: int, time in seconds that is given to the server to response until `TimeoutError exception <https://docs.python.org/3/library/exceptions.html#TimeoutError>`_ is raised

        **Return**

        None
        '''
        return self.__connector.open_camera(self.serial_number, timeout)

    def close(self, timeout=DEFAULT_TIMEOUT):
        '''

        Disconnect from the camera throught the server.
        `ValueError exception <https://docs.python.org/3/library/exceptions.html#ValueError>`_  is raised when camera is not open.


        **Params**

        * timeout: int, time in seconds that is given to the server to response until `TimeoutError exception <https://docs.python.org/3/library/exceptions.html#TimeoutError>`_ is raised

        **Return**

        None
        '''
        return self.__connector.close_camera(self.serial_number, timeout)

    def is_open(self):
        '''
        Determine whether the camera is open by the WRP server for this client.

        **Params**

        None

        **Return**

        bool
        '''
        return self.__connector.is_camera_open(self.serial_number)

    def get_frame(self, timeout=DEFAULT_TIMEOUT):
        '''

        Get a single frame from the connected camera.
        `ValueError exception <https://docs.python.org/3/library/exceptions.html#ValueError>`_  is raised when camera is not connected first.


        **Params**

        * timeout: int, time in seconds that is given to the server to response until `TimeoutError exception <https://docs.python.org/3/library/exceptions.html#TimeoutError>`_ is raised

        **Return**

        2-dimensional numpy matrix with dtype float32 containing temperature values in °C
        '''
        return self.__connector.get_frame(self.serial_number, timeout)

    def start_continuous_shot(self, callback, timeout=DEFAULT_TIMEOUT):
        '''

        Start continuous grabbing from the camera. Each frame obtained from the camera will be asynchronously passed as argument to the given callback function.
        `ValueError exception <https://docs.python.org/3/library/exceptions.html#ValueError>`_  is raised when camera is not connected first.


        **Params**

        * callback: callable, function that will be repeatedly called in its own thread for each received frame
        * timeout: int, time in seconds that is given to the server to response until `TimeoutError exception <https://docs.python.org/3/library/exceptions.html#TimeoutError>`_ is raised

        **Return**

        None
        '''
        return self.__connector.start_continuous_shot(
            self.serial_number, callback, timeout)

    def stop_continuous_shot(self, timeout=DEFAULT_TIMEOUT):
        '''

        Stop continuous grabbing from the camera.
        `ValueError exception <https://docs.python.org/3/library/exceptions.html#ValueError>`_  is raised when camera is not connected first or it is not in continuous grabbing state.


        **Params**

        * timeout: int, time in seconds that is given to the server to response until `TimeoutError exception <https://docs.python.org/3/library/exceptions.html#TimeoutError>`_ is raised

        **Return**

        None
        '''
        return self.__connector.stop_continuous_shot(
            self.serial_number, timeout)

    async def open_async(self):
        '''

        Asynchronously connect to the camera throught the server.
        `ValueError exception <https://docs.python.org/3/library/exceptions.html#ValueError>`_  is raised when another camera is already open.


        **Params**

        None

        **Return**

        None
        '''
        return await self.__connector.open_camera_async(self.serial_number)

    async def close_async(self):
        '''

        Asynchronously disconnect from the camera throught the server.
        `ValueError exception <https://docs.python.org/3/library/exceptions.html#ValueError>`_  is raised when camera is not open.


        **Params**

        None

        **Return**

        None
        '''
        return await self.__connector.close_camera_async(self.serial_number)

    async def get_frame_async(self):
        '''

        Asynchronously get a single frame from the connected camera.
        `ValueError exception <https://docs.python.org/3/library/exceptions.html#ValueError>`_  is raised when camera is not connected first.


        **Params**

        None

        **Return**

        2-dimensional numpy matrix with dtype float32 containing temperature values in °C
        '''
        return await self.__connector.get_frame_async(self.serial_number)

    async def start_continuous_shot_async(self, callback):
        '''

        Asynchronously start continuous grabbing from the camera. Each frame obtained from the camera will be asynchronously passed as argument to the given callback function.
        `ValueError exception <https://docs.python.org/3/library/exceptions.html#ValueError>`_  is raised when camera is not connected first.


        **Params**

        * callback: callable, function that will be repeatedly called in its own thread for each received frame

        **Return**

        None
        '''
        return await self.__connector.start_continuous_shot(self.serial_number, callback)

    async def stop_continuous_shot_async(self):
        '''

        Asynchronously stop continuous grabbing from the camera.
        `ValueError exception <https://docs.python.org/3/library/exceptions.html#ValueError>`_  is raised when camera is not connected first or it is not in continuous grabbing state.


        **Params**

        None

        **Return**

        None
        '''
        return await self.__connector.stop_continuous_shot(self.serial_number)
