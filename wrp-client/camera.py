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
		'Version': ('version', str) ,
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
			res += f"\n\t{attr_name}="+str(getattr(self, attr_name, default_value))
		return res+"\n"
	
	def open(self, timeout=DEFAULT_TIMEOUT):
		return self.__connector.open_camera(self.serial_number, timeout)
		
	def close(self, timeout=DEFAULT_TIMEOUT):
		return self.__connector.close_camera(self.serial_number, timeout)

	def is_open(self):
		return self.__connector.is_camera_open(self.serial_number)

	def get_frame(self, timeout=DEFAULT_TIMEOUT):
		return self.__connector.get_frame(self.serial_number, timeout)

	def start_continuous_shot(self, callback, timeout=DEFAULT_TIMEOUT):
		return self.__connector.start_continuous_shot(self.serial_number, callback, timeout)				

	def stop_continuous_shot(self, timeout=DEFAULT_TIMEOUT):
		return self.__connector.stop_continuous_shot(self.serial_number, timeout)				

		