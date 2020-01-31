import asyncio
from enum import Enum, unique
import numpy as np
import struct
import xml.etree.ElementTree as ET
from message import Message
import random
import string

# Source: https://pynative.com/python-generate-random-string/
def randomString(stringLength=10):
    """Generate a random string of fixed length """
    
    letters = string.ascii_lowercase+string.ascii_uppercase+" ,;-_" 
    return ''.join(random.choice(letters) for i in range(stringLength))

class WRPServer:

	DEFAULT_PORT = 8765
	SERVER_IP_ADDRESS = "127.0.0.1"
	class FakeCamera:
		def __init__(self):
			setattr(self, 'SerialNumber', randomString())
			setattr(self, 'ModelName', randomString(50))
			setattr(self, 'Width', random.randint(1, 1920))
			setattr(self, 'Height', random.randint(1, 1080))
			setattr(self, 'CameraMaxFPS', random.random()*30)
			setattr(self, 'Version', f"{random.randint(0, 10)}.{random.randint(0, 10)}.{random.randint(0, 10)}")
			setattr(self, 'ManufacturerInfo', randomString(100))
			setattr(self, 'VendorName', randomString(100))
	@unique
	class State(Enum):
		IDLE = 1
		CONNECTED = 2
		CAMERA_SELECTED = 3
		CONTINUOUS_GRABBING = 4

	def __init__(self, port=DEFAULT_PORT):
		self.ip_address = WRPServer.SERVER_IP_ADDRESS
		self.port = port
		self.camera_list = WRPServer.generate_random_valid_camera_list(5)
		self.state = WRPServer.State.IDLE; 

	async def run(self):
		print("Starting the server")
		self.server = await asyncio.start_server(self.routine, self.ip_address, self.port)
		print("Server has been started")
		async with self.server:
			await self.server.serve_forever()

	async def routine(self, reader, writer):
		self.__reader = reader
		self.__writer = writer
		print("Routine has started")
		self.state = WRPServer.State.CONNECTED
		while(True):
			print("Waiting for the message...")
			message = await self.receive_message()
			message_to_send = self.handle_message(message)
			if(message_to_send is not None):
				await self.send_message(message_to_send)
			else:
				print("No response to be sent was generated")

		writer.close()

	async def stop(self):
		await self.server.shutdown()
		self.server.server_close()
		del self.__reader
		del self.__writer
		del self.server 

	def handle_message(self, message):
		to_send = None
		print(f"Handling message {message} in state {self.state}")
		if(message.msg_type == Message.Type.GET_CAMERA_LIST):
			if(self.state == WRPServer.State.CONNECTED):				
				to_send = Message.create_message(Message.Type.CAMERA_LIST, xml_camera_list=self.xml_camera_list)
			else:
				to_send = Message.create_message(Message.Type.ERROR, error_code=Message.ErrorCode.UNEXPECTED_MESSAGE)

		elif(message.msg_type == Message.Type.OPEN_CAMERA):			
			if(self.state == WRPServer.State.CONNECTED):
				serial_number = getattr(message, Message.CAMERA_SERIAL_NUMBER_ATTR_NAME)
				try:
					camera = [c for c in self.camera_list if c.serial_number == serial_number][0]
					self.state = WRPServer.State.CAMERA_SELECTED
					self.camera_selected = camera
					to_send = Message.create_message(Message.Type.OK)
				except IndexError:
					to_send = Message.create_message(Message.Type.ERROR, error_code=Message.ErrorCode.CAMERA_NOT_FOUND)
			else:
				to_send = Message.create_message(Message.Type.ERROR, error_code=Message.ErrorCode.UNEXPECTED_MESSAGE)

		elif(message.msg_type == Message.Type.OPEN_CAMERA):			
			if(self.state == WRPServer.State.CONNECTED):
				serial_number = getattr(message, Message.CAMERA_SERIAL_NUMBER_ATTR_NAME)
				try:
					camera = [c for c in self.camera_list if c.serial_number == serial_number][0]
					self.state = WRPServer.State.CAMERA_SELECTED
					self.camera_selected = camera
					to_send = Message.create_message(Message.Type.OK)
				except IndexError:
					to_send = Message.create_message(Message.Type.ERROR, error_code=Message.ErrorCode.CAMERA_NOT_FOUND)
			else:
				to_send = Message.create_message(Message.Type.ERROR, error_code=Message.ErrorCode.UNEXPECTED_MESSAGE)

		elif(message.msg_type == Message.Type.CLOSE_CAMERA):			
			if(self.state == WRPServer.State.CAMERA_SELECTED):
				serial_number = getattr(message, Message.CAMERA_SERIAL_NUMBER_ATTR_NAME)
				try:
					camera = [c for c in self.camera_list if c.serial_number == serial_number][0]
					self.state = WRPServer.State.CONNECTED
					del self.camera_selected 
					to_send = Message.create_message(Message.Type.OK)
				except IndexError:
					to_send = Message.create_message(Message.Type.ERROR, error_code=Message.ErrorCode.CAMERA_NOT_FOUND)
			else:
				to_send = Message.create_message(Message.Type.ERROR, error_code=Message.ErrorCode.UNEXPECTED_MESSAGE)

		elif(message.msg_type == Message.Type.GET_FRAME):			
			if(self.state == WRPServer.State.CAMERA_SELECTED):
				serial_number = getattr(message, Message.CAMERA_SERIAL_NUMBER_ATTR_NAME)
				try:
					camera = [c for c in self.camera_list if c.serial_number == serial_number][0]
					to_send = Message.create_message(Message.Type.FRAME, )
				except IndexError:
					to_send = Message.create_message(Message.Type.ERROR, error_code=Message.ErrorCode.CAMERA_NOT_FOUND)
			else:
				to_send = Message.create_message(Message.Type.ERROR, error_code=Message.ErrorCode.UNEXPECTED_MESSAGE)
		
		else:
			print(f"Unhandled message type {message.msg_type}")
		return to_send

	async def send_message(self, message):
		print("Message to send:", message)
		self.__writer.write(message.encode())
		await self.__writer.drain()

	async def receive_message(self):
		message_type_value, payload_length = struct.unpack(">BI", await self.__reader.readexactly(Message.MESSAGE_TYPE_LENGTH + Message.PAYLOAD_SIZE_LENGTH))
		if(payload_length > 0):
			payload = await self.__reader.readexactly(payload_length)
		else:
			payload = bytes()
		response = Message.create_message_from_buffer(message_type_value=message_type_value, payload=payload, payload_length=payload_length)
		print("Received message:", response)
		return response
	

	@staticmethod
	def generate_random_valid_camera_list(number_of_cameras):
		return [WRPServer.FakeCamera() for i in range(number_of_cameras)]

	@staticmethod
	def camera_list_to_xml(camera_list):
		root = ET.Element("Cameras")
		for cam in camera_list:
			ET.SubElement(root, "Camera", **{key:str(val) for key, val in vars(cam).items()})
		return ET.tostring(root, encoding="unicode")

	@staticmethod
	def generate_random_frame(camera):
		width = getattr(camera, "Width")
		height = getattr(camera, "Height")
		frame_np =  (np.random.random((100, 100)) * 100).astype(np.float32)
		return { 
			Message.FRAME_NUMBER_ATTR_NAME: np.random.randint(0, 10), 
			Message.FRAME_TIMESTAMP_ATTR_NAME: np.random.randint(0, 2**63), 
			Message.FRAME_ATTR_NAME: frame_np 
			}
				