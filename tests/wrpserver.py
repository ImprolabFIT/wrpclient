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

	DEFAULT_PORT = 8766
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

	async def __handle_server_exception__(self):
		async with self.server as s:
			try:
				await s.serve_forever()
			except asyncio.CancelledError:
				pass
			except BaseException as e:
				print("Catched exception from the server:", e)

	async def run(self):
		self.server = await asyncio.start_server(self.routine, self.ip_address, self.port)
		self.server_task = asyncio.create_task(self.__handle_server_exception__())

	async def routine(self, reader, writer):
		self.state = WRPServer.State.CONNECTED
		while(True):
			print("Server: Waiting for the message...")
			message = await WRPServer.receive_message(reader)
			message_to_send = self.handle_message(message)
			if(message_to_send is not None):
				await WRPServer.send_message(writer, message_to_send)
			else:
				print("No response to be sent was generated")

	async def stop(self):
		self.server.close()
		await self.server.wait_closed()
		del self.server 
		self.server_task.cancel()
		await self.server_task
		del self.server_task


	def handle_message(self, message):
		to_send = None
		print(f"Server: Handling message {message} in state {self.state}")
		if(message.msg_type == Message.Type.GET_CAMERA_LIST):
			if(self.state == WRPServer.State.CONNECTED):
				to_send = Message.create_message(Message.Type.CAMERA_LIST, xml_camera_list=WRPServer.camera_list_to_xml(self.camera_list))
			else:
				to_send = Message.create_message(Message.Type.ERROR, error_code=Message.ErrorCode.UNEXPECTED_MESSAGE)

		elif(message.msg_type == Message.Type.OPEN_CAMERA):			
			if(self.state == WRPServer.State.CONNECTED):
				serial_number = getattr(message, Message.CAMERA_SERIAL_NUMBER_ATTR_NAME)
				try:
					camera = [c for c in self.camera_list if c.SerialNumber == serial_number][0]
					self.state = WRPServer.State.CAMERA_SELECTED
					self.camera_selected = camera
					to_send = Message.create_message(Message.Type.OK)
				except IndexError:
					to_send = Message.create_message(Message.Type.ERROR, error_code=Message.ErrorCode.CAMERA_NOT_FOUND)
			else:
				to_send = Message.create_message(Message.Type.ERROR, error_code=Message.ErrorCode.UNEXPECTED_MESSAGE)

		elif(message.msg_type == Message.Type.CLOSE_CAMERA):			
			if(self.state == WRPServer.State.CAMERA_SELECTED):
				self.state = WRPServer.State.CONNECTED
				del self.camera_selected
				to_send = Message.create_message(Message.Type.OK)
			else:
				to_send = Message.create_message(Message.Type.ERROR, error_code=Message.ErrorCode.UNEXPECTED_MESSAGE)

		elif(message.msg_type == Message.Type.GET_FRAME):			
			if(self.state == WRPServer.State.CAMERA_SELECTED):
				print("Server: frame_dict:", self.frame_dict)
				to_send = Message.create_message(Message.Type.FRAME, **self.frame_dict)
			else:
				to_send = Message.create_message(Message.Type.ERROR, error_code=Message.ErrorCode.UNEXPECTED_MESSAGE)
		else:
			print(f"Unhandled message type {message.msg_type}")
		return to_send

	@staticmethod
	async def send_message(writer, message):
		print("Server: Message to send:", message)
		writer.write(message.encode())
		await writer.drain()

	@staticmethod
	async def receive_message(reader):
		message_type_value, payload_length = struct.unpack(">BI", await reader.readexactly(Message.MESSAGE_TYPE_LENGTH + Message.PAYLOAD_SIZE_LENGTH))
		print(f"Server: Received message type value: {message_type_value}, payload_length: {payload_length}")
		if(payload_length > 0):
			payload = await reader.readexactly(payload_length)
		else:
			payload = bytes()
		response = Message.create_message_from_buffer(message_type_value=message_type_value, payload=payload, payload_length=payload_length)
		print("Server: Received message:", response)
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
		width = getattr(camera, "width")
		height = getattr(camera, "height")
		frame_np =  (np.random.random((100, 100)) * 100).astype(np.float32)
		return { 
			Message.FRAME_NUMBER_ATTR_NAME: np.random.randint(0, 10), 
			Message.FRAME_TIMESTAMP_ATTR_NAME: np.random.randint(0, 2**63), 
			Message.FRAME_ATTR_NAME: frame_np 
			}
				