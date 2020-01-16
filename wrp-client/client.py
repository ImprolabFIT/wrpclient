from wrp_connector import WRPConnector

class Client:
	'''
	TODO add docstring
	'''
	DEFAULT_TIMEOUT = 10
	__connector = None # (Instance of WRP Connector)

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
