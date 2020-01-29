from wrp_connector import WRPConnector

class Client:
	'''
	TODO add docstring
	'''
	DEFAULT_TIMEOUT = 10
	def __init__(self):
		self.__connector = WRPConnector()

	def connect(self, ip_address, port, timeout=DEFAULT_TIMEOUT):		
		self.__connector.connect(ip_address, port, timeout)

	def disconnect(self, timeout=DEFAULT_TIMEOUT):
		self.__connector.disconnect(timeout)

	def is_connected(self):
		return self.__connector.is_connected()

	def get_cameras(self, timeout=DEFAULT_TIMEOUT):
		return self.__connector.get_cameras(timeout)

	def get_camera(self, serial_number, timeout=DEFAULT_TIMEOUT):
		try:
			return [c for c in self.get_cameras(timeout) if c.serial_number == serial_number][0]
		except IndexError:
			raise CameraNotFound()

	async def connect_async(self, ip_address, port):		
		return self.__connector.connect_async(ip_address, port)

	async def disconnect_async(self):		
		return self.__connector.disconnect_async()

	async def get_cameras_async(self):
		return self.__connector.get_cameras_async()

	async def get_camera(self, serial_number):
		try:
			return [c for c in await self.get_cameras_async() if c.serial_number == serial_number][0]
		except IndexError:
			raise ValueError(f"No camera with serial number {serial_number} is available")
