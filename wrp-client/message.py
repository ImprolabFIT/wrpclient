from enum import Enum
import struct

class Message:
	'''
	TODO add docstring
	'''
	__buffer = bytearray()

	class Type(Enum):
		GET_CAMERAS_REQ = 1
		GET_CAMERAS_RESP = 2

	def __init__(self):
		pass

	def encode(self):
		return self.__buffer

	def __repr__(self):
		return f"{self.msg_type}({self.msg_type.value}), buffer: {self.__buffer}"

	@staticmethod
	def create_message(**kwargs):
		'''
		Create new message and set its attributes by given values. Also add this values into bytes[] with correct order.
		'''
		if("buffer" in kwargs and "msg_type" in kwargs):		
			raise ValueError("Both `msg_type` and `buffer` was defined. Choose only one!")

		if("buffer" not in kwargs and "msg_type" not in kwargs):		
			raise ValueError("Neither `msg_type` nor `buffer` was defined.")

		msg = Message()
		if("buffer" in kwargs):		
			msg.__buffer = bytes(kwargs['buffer'])
			msg.msg_type = Message.Type(struct.unpack('B', msg.__buffer)[0])
			if(msg.msg_type == Message.Type.GET_CAMERAS_RESP):
				pass
				# TODO unpack from second byte variable length string
				# struct.unpack_from("string", ...)
				#https://stackoverflow.com/questions/3753589/packing-and-unpacking-variable-length-array-string-using-the-struct-module-in-py


		if("msg_type" in kwargs):
			msg.msg_type = kwargs['msg_type']
			if(not isinstance(msg.msg_type, Message.Type)):
				if(isinstance(msg.msg_type, int)):
					msg.msg_type = Message.Type(msg.msg_type)
				else:
					raise ValueError("Parameter msg_type must be type Message.Type or int")

			msg.__buffer = struct.pack("B", msg.msg_type.value)


			# Some messages have additional info that must be withrawn from the kwargs
		return msg

	def __fill_cameras_req(self):
		pass

