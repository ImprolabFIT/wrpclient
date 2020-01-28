from enum import Enum, unique
from driver import Driver
from message import Message
import threading
import asyncio

class WRPConnector:
	'''
	TODO add docstring
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
		# Kličko kvůli nest_asyncio neboť asyncio samo o sobě nepovoluje volat run_until_complete v již běžícím event_loopu
		if(self.__state != WRPConnector.State.IDLE):
			raise ValueError("Client is already connected")

		self.__event_loop.run_until_complete(
			asyncio.wait_for(
				self.__connect(ip_address, port), 
				timeout=timeout
			)
		)
		self.__state = WRPConnector.State.CONNECTED

	def disconnect(self, timeout):
		# Kličko kvůli nest_asyncio neboť asyncio samo o sobě nepovoluje volat run_until_complete v již běžícím event_loopu
		self.__event_loop.run_until_complete(
			asyncio.wait_for(
				self.__disconnect(), 
				timeout=timeout
			)
		)

	def is_connected(self):
		return self.__state != WRPConnector.State.IDLE

	def get_cameras(self, timeout):
		return self.__event_loop.run_until_complete(
			asyncio.wait_for(
				self.__get_cameras(), 
				timeout=timeout
			)
		)

	def open_camera(self, camera_serial_number, timeout):
		self.__event_loop.run_until_complete(
			asyncio.wait_for(
				self.__open_camera(camera_serial_number), 
				timeout=timeout
			)
		)

	def is_camera_open(self, camera_serial_number):
		return camera_serial_number == self.__active_camera

	def close_camera(self, camera_serial_number, timeout):
		self.__event_loop.run_until_complete(
			asyncio.wait_for(
				self.__close_camera(camera_serial_number), 
				timeout=timeout
			)
		)

	def get_frame(self, camera_serial_number, timeout):
		return self.__event_loop.run_until_complete(
			asyncio.wait_for(
				self.__get_frame(camera_serial_number), 
				timeout=timeout
			)
		)

	def start_continuous_shot(self, camera_serial_number, callback, timeout):
		if(not callable(callback)):
			raise ValueError("Given callback must be a callable")
		self.__continuous_callback = callback
		print("Creating __continuous_thread")
		self.__continuous_thread = threading.Thread(target=self.__handle_continuous_shot_state, args=(self.__event_loop,))
		self.__event_loop.run_until_complete(
			asyncio.wait_for(
				self.__start_continuous_shot(camera_serial_number), 
				timeout=timeout
			)
		)

	def stop_continuous_shot(self, camera_serial_number, timeout):
		self.__event_loop.run_until_complete(
			asyncio.wait_for(
				self.__stop_continuous_shot(camera_serial_number), 
				timeout=timeout
			)
		)
		self.__continuous_thread = None
		self.__continuous_callback = None
		self.__last_continuous_message = None

	async def __connect(self, ip_address, port):
		await self.__driver.connect(ip_address, port)

	async def __disconnect(self):
		await self.__driver.disconnect()
		self.__state = WRPConnector.State.IDLE
		self.__active_camera = None

	async def __get_cameras(self):
		if(self.__state == WRPConnector.State.IDLE):
			raise ValueError("Client is not connected. Please call client.connect(IP_ADRRESS, PORT) first")
		if(self.__state in [WRPConnector.State.CAMERA_SELECTED, WRPConnector.State.CONTINUOUS_GRABBING]):
			serial_numbers = ", ".join(self.__active_cameras.keys())
			raise ValueError(f"Client has already selected camera with serial number {serial_numbers}. Please first disconnect it before listing all the cameras.")

		# Prepare message that is asking for list of cameras
		request = Message.create_message(message_type=Message.Type.GET_CAMERA_LIST)

		# Send it and await for complete
		await self.__driver.send_message(request)
		# Await response and check if is correct
		response = await self.__driver.receive_message()
		print("L: Message type:", response.msg_type, type(response.msg_type))
		print("R: Message type:", Message.Type.CAMERA_LIST, type(Message.Type.CAMERA_LIST))
		if(response.msg_type != Message.Type.CAMERA_LIST):
			raise ConnectionResetError(f"Something bad is happening, server responded with unexpected message {response.msg_type} (expected was {Message.Type.CAMERA_LIST})")
		return Message.xml_to_camera_list(self, getattr(response, Message.XML_CAMERA_LIST_ATTR_NAME))

	async def __open_camera(self, camera_serial_number):
		if(self.__state == WRPConnector.State.IDLE):
			raise ValueError("Client is not connected. Please call client.connect(IP_ADRRESS, PORT) first")
		
		if(camera_serial_number == self.__active_camera):
			raise ValueError(f"Camera with serial number {camera_serial_number} is already open")

		if(self.__state in [WRPConnector.State.CAMERA_SELECTED, WRPConnector.State.CONTINUOUS_GRABBING]):
			raise ValueError(f"Client has already selected camera with serial number {self.__active_camera}. Please first disconnect it before using new one.")

		request = Message.create_message(message_type=Message.Type.OPEN_CAMERA, camera_serial=camera_serial_number)
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
			raise ValueError(f"Server responded with unexpected message {response.msg_type}")

	async def __close_camera(self, camera_serial_number):
		if(self.__state == WRPConnector.State.IDLE):
			raise ValueError("Client is not connected. Please call client.connect(IP_ADRRESS, PORT) first")
		if(self.__state == WRPConnector.State.CONTINUOUS_GRABBING):
			raise ValueError(f"Client has running continuous shot. Please call camera.stop_continous_shot() first")
		if(self.__state == WRPConnector.State.CONNECTED):
			raise ValueError(f"Client is connected, but does not have a selected camera")
		if(camera_serial_number != self.__active_camera):
			raise ValueError(f"Camera with serial number {camera_serial_number} is not open")

		request = Message.create_message(message_type=Message.Type.CLOSE_CAMERA)
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
			raise ValueError(f"Server responded with unexpected message {response.msg_type}")

	async def __get_frame(self, camera_serial_number):
		if(self.__state == WRPConnector.State.IDLE):
			raise ValueError("Client is not connected. Please call client.connect(IP_ADRRESS, PORT) first")
		if(self.__state == WRPConnector.State.CONTINUOUS_GRABBING):
			raise ValueError(f"Client has running continuous shot. Please call camera.stop_continous_shot() first")
		if(self.__state == WRPConnector.State.CONNECTED):
			raise ValueError(f"Client is connected, but does not have a selected camera")
		if(not camera_serial_number == self.__active_camera):
			raise ValueError(f"Camera with serial number {camera_serial_number} is not open")

		request = Message.create_message(message_type=Message.Type.GET_FRAME)
		await self.__driver.send_message(request)
		# Await response and check if is correct
		response = await self.__driver.receive_message()
		if(response.msg_type == Message.Type.FRAME):
			frame = getattr(response, Message.FRAME_ATTR_NAME)
			frame_timestamp = getattr(response, Message.FRAME_TIMESTAMP_ATTR_NAME)
			self.__state = WRPConnector.State.CAMERA_SELECTED
			return frame, frame_timestamp
		elif(response.msg_type == Message.Type.ERROR):
			error_code = getattr(response, ERROR_CODE_ATTR_NAME)
			self.__state = WRPConnector.State.CAMERA_SELECTED
			raise ValueError(f"Server responded with error code {error_code}")
		else:
			raise ValueError(f"Server responded with unexpected message {response.msg_type}")

	
	async def __start_continuous_shot(self, camera_serial_number):
		if(self.__state == WRPConnector.State.IDLE):
			raise ValueError("Client is not connected. Please call client.connect(IP_ADRRESS, PORT) first")
		if(self.__state == WRPConnector.State.CONTINUOUS_GRABBING):
			raise ValueError(f"Client already has running continuous shot")
		if(self.__state == WRPConnector.State.CONNECTED):
			raise ValueError(f"Client is connected, but does not have a selected camera")
		if(not camera_serial_number == self.__active_camera):
			raise ValueError(f"Camera with serial number {camera_serial_number} is not open")

		request = Message.create_message(message_type=Message.Type.START_CONTINUOUS_GRABBING)
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
			raise ValueError(f"Server responded with unexpected message {response.msg_type}")
		print("Starting __continuous_thread")
		self.__continuous_thread.start()

	async def __stop_continuous_shot(self, camera_serial_number):
		if(self.__state == WRPConnector.State.IDLE):
			raise ValueError("Client is not connected. Please call client.connect(IP_ADRRESS, PORT) first")
		if(self.__state == WRPConnector.State.CAMERA_SELECTED):
			raise ValueError(f"Client has selected camera but has not sent START_CONTINUOUS_GRABBING message")
		if(self.__state == WRPConnector.State.CONNECTED):
			raise ValueError(f"Client is connected, but does not have a selected camera")
		if(not camera_serial_number == self.__active_camera):
			raise ValueError(f"Camera with serial number {camera_serial_number} is not open")

		print("Setting __continuous_shot_aborted=True")
		self.__continuous_shot_aborted = True
		print("Sending STOP_CONTINUOUS_GRABBING message")
		request = Message.create_message(message_type=Message.Type.STOP_CONTINUOUS_GRABBING)
		await self.__driver.send_message(request)
		print("Joining __continuous_thread")
		self.__continuous_thread.join()

		if(self.__continuous_last_message is not None):
			if(self.__continuous_last_message.msg_type == Message.Type.OK):
				self.__state = WRPConnector.State.CAMERA_SELECTED
			elif(self.__continuous_last_message.msg_type == Message.Type.ERROR):
				error_code = getattr(self.__continuous_last_message, ERROR_CODE_ATTR_NAME)
				self.__state = WRPConnector.State.CONTINUOUS_GRABBING
				raise ValueError(f"Server responded with error code {error_code}")
			else:
				raise ValueError(f"Server responded with unexpected message {self.__continuous_last_message.msg_type}")
		else:
			raise ValueError(f"Server has not responded to STOP_CONTINUOUS_GRABBING message")


	def __handle_continuous_shot_state(self, event_loop):
		print("Entering to __handle_continuous_shot_state")
		asyncio.set_event_loop(event_loop)
		event_loop.run_until_complete(self.__handle_continuous_shot_state_async())
		
	async def __handle_continuous_shot_state_async(self):
		print("Entering to __handle_continuous_shot_state_async")
		while(True):
			print("Awaiting message to receive")
			response = await self.__driver.receive_message()
			print(f"Message {response} received")
			if(response.msg_type in [Message.Type.OK, Message.Type.ERROR]):
				if(self.__continuous_shot_aborted):
					self.__continuous_last_message = response
					print("Filling __continuous_last_message")
					break
				else:
					raise ValueError(f"Server responded with unexpected message {response.msg_type} when continuous shot was not aborted")
			elif(response.msg_type == Message.Type.FRAME):
				if(self.__continuous_shot_aborted):
					pass
				else:
					print("Calling callback")
			else:
				raise ValueError(f"Server responded with unexpected message {response.msg_type}")
	
