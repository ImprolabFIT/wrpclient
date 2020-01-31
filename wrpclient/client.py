from .wrp_connector import WRPConnector


class Client:
    '''
    Represents client that can establish connection with the WRP server and ask for the list of available cameras
    '''
    DEFAULT_TIMEOUT = 10
    DEFAULT_PORT = 8754

    def __init__(self):
        self.__connector = WRPConnector()

    def connect(self, ip_address, port=DEFAULT_PORT, timeout=DEFAULT_TIMEOUT):
        '''
        Connect client to the server with given IP address and port.
        `ValueError exception <https://docs.python.org/3/library/exceptions.html#ValueError>`_  is raised when client is already connected.

        **Params**

        * ip_address: str, IP address of the WRP server
        * port: int, port of the WRP server
        * timeout: int, time in seconds that is given to the server to response until `TimeoutError exception <https://docs.python.org/3/library/exceptions.html#TimeoutError>`_ is raised

        **Return**

        None
        '''
        self.__connector.connect(ip_address, port, timeout)

    def disconnect(self, timeout=DEFAULT_TIMEOUT):
        '''
        Disconnect client from the server.
        `ValueError exception <https://docs.python.org/3/library/exceptions.html#ValueError>`_  is raised when client is not connected.

        **Params**

        * timeout: int, time in seconds that is given to the server to response until `TimeoutError exception <https://docs.python.org/3/library/exceptions.html#TimeoutError>`_ is raised

        **Return**

        None
        '''
        self.__connector.disconnect(timeout)

    def is_connected(self):
        '''
        Determine whether client is connected to the WRP server.

        **Params**

        None

        **Return**

        bool
        '''
        return self.__connector.is_connected()

    def get_cameras(self, timeout=DEFAULT_TIMEOUT):
        '''
        Get list of all cameras connected to the server. First client must be connected to the server.
        If he is not in the connected state, `ValueError exception <https://docs.python.org/3/library/exceptions.html#ValueError>`_  is raised.


        **Params**

        * timeout: int, time in seconds that is given to the server to response until `TimeoutError exception <https://docs.python.org/3/library/exceptions.html#TimeoutError>`_ is raised

        **Return**

        list of instances of :class:`Camera`
        '''
        return self.__connector.get_cameras(timeout)

    def get_camera(self, serial_number, timeout=DEFAULT_TIMEOUT):
        '''
        Get camera with the given serial number. First client must be connected to the server.
        If he is not in the connected state, `ValueError exception <https://docs.python.org/3/library/exceptions.html#ValueError>`_  is raised.
        If there is no camera with the given serial number available, `ValueError exception <https://docs.python.org/3/library/exceptions.html#ValueError>`_ is also raised.

        **Params**

        * timeout: int, time in seconds that is given to the server to response until `TimeoutError exception <https://docs.python.org/3/library/exceptions.html#TimeoutError>`_ is raised

        **Return**

        instance of :class:`Camera`
        '''
        try:
            return [c for c in self.get_cameras(
                timeout) if c.serial_number == serial_number][0]
        except IndexError:
            raise ValueError(
                f"No camera with serial number {serial_number} is available")

    async def connect_async(self, ip_address, port):
        '''
        Asynchronously connect client to the server with given IP address and port.
        `ValueError exception <https://docs.python.org/3/library/exceptions.html#ValueError>`_  is raised when client is already connected.

        **Params**

        * ip_address: str, IP address of the WRP server
        * port: int, port of the WRP server

        **Return**

        None
        '''
        return await self.__connector.connect_async(ip_address, port)

    async def disconnect_async(self):
        '''
        Asynchronously disconnect client from the server.
        `ValueError exception <https://docs.python.org/3/library/exceptions.html#ValueError>`_  is raised when client is not connected.

        **Params**

        None

        **Return**

        None
        '''
        return await self.__connector.disconnect_async()

    async def get_cameras_async(self):
        '''

        Asynchronously get list of all cameras connected to the server. First client must be connected to the server.
        If he is not in the connected state, `ValueError exception <https://docs.python.org/3/library/exceptions.html#ValueError>`_  is raised.

        **Params**

        None

        **Return**

        list of instances of :class:`Camera`
        '''
        return await self.__connector.get_cameras_async()

    async def get_camera_async(self, serial_number):
        '''

        Get camera with the given serial number. First client must be connected to the server.
        If he is not in the connected state, `ValueError exception <https://docs.python.org/3/library/exceptions.html#ValueError>`_  is raised.
        If there is no camera with the given serial number available, `ValueError exception <https://docs.python.org/3/library/exceptions.html#ValueError>`_ is also raised.

        **Params**

        None

        **Return**

        instance of :class:`Camera`
        '''
        try:
            return [c for c in await self.get_cameras_async() if c.serial_number == serial_number][0]
        except IndexError:
            raise ValueError(
                f"No camera with serial number {serial_number} is available")
