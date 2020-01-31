from enum import Enum, unique
import threading
import asyncio
from .driver import Driver
from .message import Message


class WRPConnector:
    '''
    Finite-state machine that implements WRP and works like a middleman between cameras and driver.
    '''
    @unique
    class State(Enum):
        IDLE = 1
        CONNECTED = 2
        CAMERA_SELECTED = 3
        CONTINUOUS_GRABBING = 4

    def __init__(self):
        self.__driver = Driver()
        self.__state = WRPConnector.State.IDLE
        self.__event_loop = asyncio.get_event_loop()
        self.__active_camera = None
        self.__continuous_shot_aborted = False
        self.__continuous_callback = None
        self.__continuous_thread = None
        self.__continuous_last_message = None

    def connect(self, ip_address, port, timeout):
        '''
        Moves from state IDLE to state CONNECTED if the connection with the server is established within the timeout.

        **Params**

        * ip_address: str, IP address of the WRP server
        * port: int, port of the WRP server
        * timeout: int, time in seconds that is given to the server to response until `TimeoutError exception <https://docs.python.org/3/library/exceptions.html#TimeoutError>`_ is raised

        **Return**

        None
        '''
        self.__event_loop.run_until_complete(
            asyncio.wait_for(
                self.connect_async(ip_address, port),
                timeout=timeout
            )
        )

    def disconnect(self, timeout):
        '''
        Moves from state CONNECTED to state IDLE if the server confirms the request within the timeout.

        **Params**

        * timeout: int, time in seconds that is given to the server to response until `TimeoutError exception <https://docs.python.org/3/library/exceptions.html#TimeoutError>`_ is raised

        **Return**

        None
        '''
        self.__event_loop.run_until_complete(
            asyncio.wait_for(
                self.disconnect_async(),
                timeout=timeout
            )
        )

    def is_connected(self):
        '''
        Check if connection was established

        **Params**

        None

        **Return**

        bool
        '''
        return self.__state != WRPConnector.State.IDLE

    def get_cameras(self, timeout):
        '''
        Moves from state CONNECTED to state WAITING_FOR_CAMERA_LIST and back if the server sends response on the request within the timeout.

        **Params**

        * timeout: int, time in seconds that is given to the server to response until `TimeoutError exception <https://docs.python.org/3/library/exceptions.html#TimeoutError>`_ is raised

        **Return**

        None
        '''
        return self.__event_loop.run_until_complete(
            asyncio.wait_for(
                self.get_cameras_async(),
                timeout=timeout
            )
        )

    def open_camera(self, camera_serial_number, timeout):
        '''
        Moves from state CONNECTED to state CAMERA_SELECTED if the server sends response on the request within the timeout.

        **Params**

        * camera_serial_number: str
        * timeout: int, time in seconds that is given to the server to response until `TimeoutError exception <https://docs.python.org/3/library/exceptions.html#TimeoutError>`_ is raised

        **Return**

        None
        '''
        self.__event_loop.run_until_complete(
            asyncio.wait_for(
                self.open_camera_async(camera_serial_number),
                timeout=timeout
            )
        )

    def is_camera_open(self, camera_serial_number):
        '''
        Check if the camera with a given serial number is open.

        **Params**

        * camera_serial_number: str

        **Return**

        bool
        '''
        return camera_serial_number == self.__active_camera

    def close_camera(self, camera_serial_number, timeout):
        '''
        Moves from state CAMERA_SELECTED to state CONNECTED if the server sends response on the request within the timeout.

        **Params**

        * camera_serial_number: str
        * timeout: int, time in seconds that is given to the server to response until `TimeoutError exception <https://docs.python.org/3/library/exceptions.html#TimeoutError>`_ is raised

        **Return**

        None
        '''
        self.__event_loop.run_until_complete(
            asyncio.wait_for(
                self.close_camera_async(camera_serial_number),
                timeout=timeout
            )
        )

    def get_frame(self, camera_serial_number, timeout):
        '''
        Moves from state CAMERA_SELECTED to state WAITING_FOR_FRAME and back if the server sends response on the request within the timeout.

        **Params**

        * camera_serial_number: str
        * timeout: int, time in seconds that is given to the server to response until `TimeoutError exception <https://docs.python.org/3/library/exceptions.html#TimeoutError>`_ is raised

        **Return**

        None
        '''
        return self.__event_loop.run_until_complete(
            asyncio.wait_for(
                self.get_frame_async(camera_serial_number),
                timeout=timeout
            )
        )

    def start_continuous_shot(self, camera_serial_number, callback, timeout):
        '''
        Moves from state CAMERA_SELECTED to state CONTINUOUS_GRABBING if the server sends response on the request within the timeout.

        **Params**

        * camera_serial_number: str
        * callback: callable
        * timeout: int, time in seconds that is given to the server to response until `TimeoutError exception <https://docs.python.org/3/library/exceptions.html#TimeoutError>`_ is raised

        **Return**

        None
        '''
        self.__event_loop.run_until_complete(
            asyncio.wait_for(
                self.start_continuous_shot_async(camera_serial_number),
                timeout=timeout
            )
        )

    def stop_continuous_shot(self, camera_serial_number, timeout):
        '''
        Moves from state CONTINUOUS_GRABBING to state CAMERA_SELECTED if the server sends response on the request within the timeout.

        **Params**

        * camera_serial_number: str
        * timeout: int, time in seconds that is given to the server to response until `TimeoutError exception <https://docs.python.org/3/library/exceptions.html#TimeoutError>`_ is raised

        **Return**

        None
        '''
        self.__event_loop.run_until_complete(
            asyncio.wait_for(
                self.stop_continuous_shot_async(camera_serial_number),
                timeout=timeout
            )
        )

    async def connect_async(self, ip_address, port):
        '''
        Asynchronously moves from state IDLE to state CONNECTED.

        **Params**

        * ip_address: str, IP address of the WRP server
        * port: int, port of the WRP server

        **Return**

        None
        '''
        if(self.__state != WRPConnector.State.IDLE):
            raise ValueError("Client is already connected")
        await self.__driver.connect(ip_address, port)
        self.__state = WRPConnector.State.CONNECTED

    async def disconnect_async(self):
        '''
        Asynchronously moves from state CONNECTED to state IDLE.
        **Params**

        None

        **Return**

        None
        '''
        await self.__driver.disconnect()
        self.__state = WRPConnector.State.IDLE
        self.__active_camera = None

    async def get_cameras_async(self):
        '''
        Asynchronously moves from state CONNECTED to state WAITING_FOR_CAMERA_LIST and back.

        **Params**

        None

        **Return**

        None
        '''
        if(self.__state == WRPConnector.State.IDLE):
            raise ValueError(
                "Client is not connected. Please call client.connect(IP_ADRRESS, PORT) first")
        if(self.__state in [WRPConnector.State.CAMERA_SELECTED, WRPConnector.State.CONTINUOUS_GRABBING]):
            serial_numbers = ", ".join(self.__active_cameras.keys())
            raise ValueError(
                f"Client has already selected camera with serial number {serial_numbers}. Please first disconnect it before listing all the cameras.")

        # Prepare message that is asking for list of cameras
        request = Message.create_message(
            message_type=Message.Type.GET_CAMERA_LIST)

        # Send it and await for complete
        await self.__driver.send_message(request)
        # Await response and check if is correct
        response = await self.__driver.receive_message()
        if(response.msg_type != Message.Type.CAMERA_LIST):
            raise ConnectionResetError(
                f"Something bad is happening, server responded with unexpected message {response.msg_type} (expected was {Message.Type.CAMERA_LIST})")
        return Message.xml_to_camera_list(self, getattr(
            response, Message.XML_CAMERA_LIST_ATTR_NAME))

    async def open_camera_async(self, camera_serial_number):
        '''
        Asynchronously moves from state CONNECTED to state CAMERA_SELECTED.

        **Params**

        * camera_serial_number: str

        **Return**

        None
        '''
        if(self.__state == WRPConnector.State.IDLE):
            raise ValueError(
                "Client is not connected. Please call client.connect(IP_ADRRESS, PORT) first")

        if(camera_serial_number == self.__active_camera):
            raise ValueError(
                f"Camera with serial number {camera_serial_number} is already open")

        if(self.__state in [WRPConnector.State.CAMERA_SELECTED, WRPConnector.State.CONTINUOUS_GRABBING]):
            raise ValueError(
                f"Client has already selected camera with serial number {self.__active_camera}. Please first disconnect it before using new one.")

        request = Message.create_message(
            message_type=Message.Type.OPEN_CAMERA,
            camera_serial=camera_serial_number)
        await self.__driver.send_message(request)
        # Await response and check if is correct
        response = await self.__driver.receive_message()
        if(response.msg_type == Message.Type.OK):
            self.__active_camera = camera_serial_number
            self.__state = WRPConnector.State.CAMERA_SELECTED
        elif(response.msg_type == Message.Type.ERROR):
            error_code = getattr(response, ERROR_CODE_ATTR_NAME)
            raise ValueError(f"Server responded with error code {error_code}")
        else:
            raise ValueError(
                f"Server responded with unexpected message {response.msg_type}")

    async def close_camera_async(self, camera_serial_number):
        '''
        Asynchronously moves from state CAMERA_SELECTED to state CONNECTED.

        **Params**

        * camera_serial_number: str

        **Return**

        None
        '''
        if(self.__state == WRPConnector.State.IDLE):
            raise ValueError(
                "Client is not connected. Please call client.connect(IP_ADRRESS, PORT) first")
        if(self.__state == WRPConnector.State.CONTINUOUS_GRABBING):
            raise ValueError(
                f"Client has running continuous shot. Please call camera.stop_continous_shot() first")
        if(self.__state == WRPConnector.State.CONNECTED):
            raise ValueError(
                f"Client is connected, but does not have a selected camera")
        if(camera_serial_number != self.__active_camera):
            raise ValueError(
                f"Camera with serial number {camera_serial_number} is not open")

        request = Message.create_message(
            message_type=Message.Type.CLOSE_CAMERA)
        await self.__driver.send_message(request)
        # Await response and check if is correct
        response = await self.__driver.receive_message()
        if(response.msg_type == Message.Type.OK):
            self.__active_camera = None
            self.__state = WRPConnector.State.CONNECTED
        elif(response.msg_type == Message.Type.ERROR):
            error_code = getattr(response, ERROR_CODE_ATTR_NAME)
            raise ValueError(f"Server responded with error code {error_code}")
        else:
            raise ValueError(
                f"Server responded with unexpected message {response.msg_type}")

    async def get_frame_async(self, camera_serial_number):
        '''
        Asynchronously moves from state CAMERA_SELECTED to state WAITING_FOR_FRAME and back.

        **Params**

        * camera_serial_number: str

        **Return**

        None
        '''

        if(self.__state == WRPConnector.State.IDLE):
            raise ValueError(
                "Client is not connected. Please call client.connect(IP_ADRRESS, PORT) first")
        if(self.__state == WRPConnector.State.CONTINUOUS_GRABBING):
            raise ValueError(
                f"Client has running continuous shot. Please call camera.stop_continous_shot() first")
        if(self.__state == WRPConnector.State.CONNECTED):
            raise ValueError(
                f"Client is connected, but does not have a selected camera")
        if(not camera_serial_number == self.__active_camera):
            raise ValueError(
                f"Camera with serial number {camera_serial_number} is not open")

        request = Message.create_message(message_type=Message.Type.GET_FRAME)
        await self.__driver.send_message(request)
        # Await response and check if is correct
        response = await self.__driver.receive_message()
        if(response.msg_type == Message.Type.FRAME):
            frame = getattr(response, Message.FRAME_ATTR_NAME)
            frame_timestamp = getattr(
                response, Message.FRAME_TIMESTAMP_ATTR_NAME)
            self.__state = WRPConnector.State.CAMERA_SELECTED
            return frame, frame_timestamp
        elif(response.msg_type == Message.Type.ERROR):
            error_code = getattr(response, ERROR_CODE_ATTR_NAME)
            self.__state = WRPConnector.State.CAMERA_SELECTED
            raise ValueError(f"Server responded with error code {error_code}")
        else:
            raise ValueError(
                f"Server responded with unexpected message {response.msg_type}")

    async def start_continuous_shot_async(self, camera_serial_number):
        '''
        Asynchronously moves from state CAMERA_SELECTED to state CONTINUOUS_GRABBING.

        **Params**

        * camera_serial_number: str

        **Return**

        None
        '''
        if(not callable(callback)):
            raise ValueError("Given callback must be a callable")
        self.__continuous_callback = callback
        self.__continuous_thread = threading.Thread(
            target=self.__handle_continuous_shot_state, args=(
                self.__event_loop,))

        if(self.__state == WRPConnector.State.IDLE):
            raise ValueError(
                "Client is not connected. Please call client.connect(IP_ADRRESS, PORT) first")
        if(self.__state == WRPConnector.State.CONTINUOUS_GRABBING):
            raise ValueError(f"Client already has running continuous shot")
        if(self.__state == WRPConnector.State.CONNECTED):
            raise ValueError(
                f"Client is connected, but does not have a selected camera")
        if(not camera_serial_number == self.__active_camera):
            raise ValueError(
                f"Camera with serial number {camera_serial_number} is not open")

        request = Message.create_message(
            message_type=Message.Type.START_CONTINUOUS_GRABBING)
        await self.__driver.send_message(request)
        # Await response and check if is correct
        response = await self.__driver.receive_message()
        if(response.msg_type == Message.Type.OK):
            self.__state = WRPConnector.State.CONTINUOUS_GRABBING
        elif(response.msg_type == Message.Type.ERROR):
            error_code = getattr(response, ERROR_CODE_ATTR_NAME)
            self.__state = WRPConnector.State.CAMERA_SELECTED
            raise ValueError(f"Server responded with error code {error_code}")
        else:
            raise ValueError(
                f"Server responded with unexpected message {response.msg_type}")
        self.__continuous_thread.start()

    async def stop_continuous_shot_async(self, camera_serial_number):
        '''
        Asynchronously moves from state CONTINUOUS_GRABBING to state CAMERA_SELECTED.

        **Params**

        * camera_serial_number: str

        **Return**

        None
        '''
        if(self.__state == WRPConnector.State.IDLE):
            raise ValueError(
                "Client is not connected. Please call client.connect(IP_ADRRESS, PORT) first")
        if(self.__state == WRPConnector.State.CAMERA_SELECTED):
            raise ValueError(
                f"Client has selected camera but has not sent START_CONTINUOUS_GRABBING message")
        if(self.__state == WRPConnector.State.CONNECTED):
            raise ValueError(
                f"Client is connected, but does not have a selected camera")
        if(not camera_serial_number == self.__active_camera):
            raise ValueError(
                f"Camera with serial number {camera_serial_number} is not open")

        self.__continuous_shot_aborted = True
        request = Message.create_message(
            message_type=Message.Type.STOP_CONTINUOUS_GRABBING)
        await self.__driver.send_message(request)
        self.__continuous_thread.join()

        if(self.__continuous_last_message is not None):
            if(self.__continuous_last_message.msg_type == Message.Type.OK):
                self.__state = WRPConnector.State.CAMERA_SELECTED
            elif(self.__continuous_last_message.msg_type == Message.Type.ERROR):
                error_code = getattr(
                    self.__continuous_last_message,
                    ERROR_CODE_ATTR_NAME)
                self.__state = WRPConnector.State.CONTINUOUS_GRABBING
                raise ValueError(
                    f"Server responded with error code {error_code}")
            else:
                raise ValueError(
                    f"Server responded with unexpected message {self.__continuous_last_message.msg_type}")
        else:
            raise ValueError(
                f"Server has not responded to STOP_CONTINUOUS_GRABBING message")

        self.__continuous_thread = None
        self.__continuous_callback = None
        self.__last_continuous_message = None

    def __handle_continuous_shot_state(self, event_loop):
        asyncio.set_event_loop(event_loop)
        event_loop.run_until_complete(
            self.__handle_continuous_shot_state_async())

    async def __handle_continuous_shot_state_async(self):
        while(True):
            response = await self.__driver.receive_message()
            if(response.msg_type in [Message.Type.OK, Message.Type.ERROR]):
                if(self.__continuous_shot_aborted):
                    self.__continuous_last_message = response
                    break
                else:
                    raise ValueError(
                        f"Server responded with unexpected message {response.msg_type} when continuous shot was not aborted")
            elif(response.msg_type == Message.Type.FRAME):
                pass
            else:
                raise ValueError(
                    f"Server responded with unexpected message {response.msg_type}")
