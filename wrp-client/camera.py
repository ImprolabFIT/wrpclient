class Camera:
	'''
	TODO add docstring
	'''
	serial_number = ""
	model_name = ""
	vendor_name = ""
	__connector = None # (Instance of WRP Connector)

	def __init__(self, connector, serial_number, model_name, vendor_name):
		self.__connector = connector
		self.serial_number = serial_number
		self.model_name = model_name
		self.vendor_name = vendor_name

	def open(self):
		pass

	def close(self):
		pass

	def is_open(self):
		pass

	def get_frame(self):
		pass

	def start_continuous_shot(self, callback):
		pass				

	def stop_continous_shot(self):
		pass

	def is_grabbing(self):
		pass
