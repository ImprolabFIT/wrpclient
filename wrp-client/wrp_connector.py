from enum import Enum
from driver import Driver
from message import Message
import asyncio

class WRPConnector:
	'''
	TODO add docstring
	'''
	__event_loop = None
	__state = None
	__driver = None
	__client_id = None
	__driver = None # (Instance of WRP Connector)

	class State(Enum):
		IDLE = 1
		CONNECTED = 2

	def __init__(self):
		self.__driver = Driver() 
		self.__state = self.State.IDLE
		self.__event_loop = asyncio.get_event_loop()
	
	def connect(self, ip_address, port, timeout):
		# Kličko kvůli nest_asyncio neboť asyncio samo o sobě nepovoluje volat run_until_complete v již běžícím event_loopu
		if(self.__state != self.State.IDLE):
			raise ValueError("Client is already connected")

		self.__event_loop.run_until_complete(
			asyncio.wait_for(
				self.__connect(ip_address, port), 
				timeout=timeout
			)
		)
		self.__state = self.State.CONNECTED

	def disconnect(self, timeout):
		# Kličko kvůli nest_asyncio neboť asyncio samo o sobě nepovoluje volat run_until_complete v již běžícím event_loopu
		self.__event_loop.run_until_complete(
			asyncio.wait_for(
				self.__disconnect(), 
				timeout=timeout
			)
		)

	def is_connected(self):
		return self.__state != self.State.IDLE

	def get_cameras(self, timeout):
		self.__event_loop.run_until_complete(
			asyncio.wait_for(
				self.__get_cameras(), 
				timeout=timeout
			)
		)

	async def __connect(self, ip_address, port):
		await self.__driver.connect(ip_address, port)

	async def __disconnect(self):
		await self.__driver.disconnect()

	async def __get_cameras(self):
		# Check if state is connected - maybe it will be automatical
		if(self.__state != self.State.CONNECTED):
			raise ValueError("Client is not connected. Please call client.connect(IP_ADRRESS, PORT) first")

		# Prepare message that is asking for list of cameras
		request = Message.create_message(msg_type=Message.Type.GET_CAMERAS_REQ)
		# Send it and await for complete
		await self.__driver.send_message(request)
		# Await response and check if is correct
		response = await self.__driver.receive_message()
		if(response.msg_type != Message.Type.GET_CAMERAS_RESP):
			raise ConnectionResetError(f"Something bad is happening, server responded with unexpected message {response.type} (expected was {Message.TYPE.GIVE_CAMERAS}")
		# Withraw and return in in list
		return response.cameras

