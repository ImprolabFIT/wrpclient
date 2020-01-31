from enum import Enum, unique
import struct
import numpy as np
import xml.etree.ElementTree as ET
from .camera import Camera


class Message:
    '''
    Structure that implements WRP message and is used for passing all the information at once
    '''

    PAYLOAD_SIZE_LENGTH = 4
    MESSAGE_TYPE_LENGTH = 1

    ERROR_CODE_ATTR_NAME = 'error_code'
    XML_CAMERA_LIST_ATTR_NAME = 'xml_camera_list'
    CAMERA_SERIAL_NUMBER_ATTR_NAME = 'camera_serial'
    FRAME_NUMBER_ATTR_NAME = 'frame_number'
    FRAME_TIMESTAMP_ATTR_NAME = 'frame_timestamp'
    FRAME_ATTR_NAME = 'frame'

    @unique
    class Type(Enum):
        INVALID = 0
        OK = 1
        ERROR = 2
        GET_CAMERA_LIST = 3
        CAMERA_LIST = 4
        OPEN_CAMERA = 5
        CLOSE_CAMERA = 6
        GET_FRAME = 7
        FRAME = 8
        START_CONTINUOUS_GRABBING = 9
        STOP_CONTINUOUS_GRABBING = 10
        ACK_CONTINUOUS_GRABBING = 11

    def __init__(self):
        self.__buffer = bytearray()

    def encode(self):
        '''
        Encode message along its attributes (message type, payload etc.) to bytearray

        **Params**

        None

        **Return**

        bytearray containing encoded message
        '''
        return self.__buffer

    def __repr__(self):
        if(len(self.__buffer) > 500):
            return f"{self.msg_type}({self.msg_type.value}), buffer (trimmed): {self.__buffer[:500]}"
        else:
            return f"{self.msg_type}({self.msg_type.value}), buffer: {self.__buffer}"

    @staticmethod
    def is_int_valid_message_type(message_type_value):
        '''
        Static method that checks if a given integer represents valid message type

        **Params**

        * message_type_value: int

        **Return**

        bool
        '''
        return message_type_value in [
            t.value for t in Message.Type if t.name != "INVALID"]

    @staticmethod
    def convert_int_to_message_type(message_type_value):
        '''
        Static method that converts a given integer to the Message.Type enum
        `ValueError exception <https://docs.python.org/3/library/exceptions.html#ValueError>`_  when a given integer is not associated with any Message.Type.

        **Params**

        * message_type_value: int

        **Return**

        Message.Type enum
        '''
        if(not isinstance(message_type_value, int)):
            raise ValueError("Parameter message_type_value must be int")

        if(not Message.is_int_valid_message_type(message_type_value)):
            raise ValueError(f"Unkown message type value {message_type_value}")

        return Message.Type(message_type_value)

#	@staticmethod
#	def extract_payload_length_from_payload(payload, message_type):
#		if(len(payload) < Message.PAYLOAD_SIZE_LENGTH):
#			raise ValueError(f"Length of the payload for Message with type {message_type} should be at least {Message.PAYLOAD_SIZE_LENGTH}, not {len(payload)}")
#		payload_length, = struct.unpack(">I", payload)
#
#		if(len(payload) != payload_length):
#			raise ValueError(f"Length of the payload acccording to first four bytes is {payload_length}, but given payload has length {len(payload)}")
#		return payload_length

    @staticmethod
    def create_message_from_buffer(
            message_type_value,
            payload=bytes(),
            payload_length=0):
        '''
        Static method that checks if the given message type and payload extracted from a socket correct and decompose it to attributes specific for each message type
        `ValueError exception <https://docs.python.org/3/library/exceptions.html#ValueError>`_  is raised when given payload's length and payload_length does not match according to WRP.

        **Params**

        * message_type_value: int, code of the message type
        * payload: bytes, extracted from the socket
        * payload_length: int, length of the payload according to received bytes from the socket

        **Return**

        instance of :class:`Message`
        '''
        if(len(payload) != payload_length):
            raise ValueError(
                f"Given payload's length is {len(payload)} but payload_length={payload_length}")

        msg = Message()
        msg.msg_type = Message.convert_int_to_message_type(message_type_value)

        t = Message.Type
        already_read = 0
        if(msg.msg_type in [t.OK, t.GET_CAMERA_LIST]):
            pass

        elif(msg.msg_type == t.ERROR):
            error_code, = struct.unpack_from(">B", payload, already_read)
            setattr(msg, Message.ERROR_CODE_ATTR_NAME, error_code)
            already_read += struct.calcsize(">B")

        elif(msg.msg_type == t.CAMERA_LIST):
            xml_camera_list, = struct.unpack_from(
                f">{payload_length}s", payload, already_read)
            setattr(
                msg,
                Message.XML_CAMERA_LIST_ATTR_NAME,
                xml_camera_list.decode('ASCII'))
            already_read += struct.calcsize(f">{payload_length}s")

        elif(msg.msg_type == t.OPEN_CAMERA):
            serial_number, = struct.unpack_from(
                f">{payload_length}s", payload, already_read)
            setattr(
                msg,
                Message.CAMERA_SERIAL_NUMBER_ATTR_NAME,
                serial_number.decode('ASCII'))
            already_read += struct.calcsize(f">{payload_length}s")

        elif(msg.msg_type in [t.FRAME, t.ACK_CONTINUOUS_GRABBING]):
            if(msg.msg_type in [t.FRAME, t.ACK_CONTINUOUS_GRABBING]):
                frame_number, = struct.unpack_from(">I", payload, already_read)
                setattr(msg, Message.FRAME_NUMBER_ATTR_NAME, frame_number)
                already_read += struct.calcsize(">I")

            if(msg.msg_type == t.FRAME):
                timestamp, frame_height, frame_width = struct.unpack_from(
                    ">QHH", payload, already_read)
                setattr(msg, Message.FRAME_TIMESTAMP_ATTR_NAME, timestamp)
                already_read += struct.calcsize(">QHH")

                frame_flatten = struct.unpack_from(
                    f">{frame_height*frame_width}f", payload, already_read)
                frame = np.array(
                    frame_flatten,
                    dtype=np.float32).reshape(
                    frame_height,
                    frame_width)
                setattr(msg, Message.FRAME_ATTR_NAME, frame)
                already_read += struct.calcsize(f"{frame_height*frame_width}f")

        else:
            raise ValueError(f"Unknown message type {msg.msg_type}")

        if(already_read != payload_length):
            raise ValueError(
                f"Deserialization of the message is finished, but no all bytes in payload were used. "
                f"payload_length={payload_length}, number of read bytes={already_read}, message type={msg.msg_type}")
        msg.__buffer = struct.pack(
            f">BI",
            message_type_value,
            payload_length) + payload
        return msg

    @staticmethod
    def create_message(message_type, **kwargs):
        '''
        Static method that creates new message and sets its attributes by given values. Also add this values into bytes[] with correct order.
        `ValueError exception <https://docs.python.org/3/library/exceptions.html#ValueError>`_  is raised message type and other attributes does not match according to WRP.

        **Params**

        * message_type: Message.Type
        * kwargs: dict that should contain values depending on the type of the message

        **Return**

        instance of :class:`Message`
        '''
        if(not isinstance(message_type, Message.Type)):
            raise ValueError(
                "Parameter message_type must be type Message.Type")
        msg = Message()
        msg.msg_type = message_type
        msg.__buffer = struct.pack(">B", msg.msg_type.value)

        payload_content = bytes()
        t = Message.Type
        if(msg.msg_type in [t.OK, t.GET_CAMERA_LIST, t.CLOSE_CAMERA, t.GET_FRAME, t.START_CONTINUOUS_GRABBING, t.STOP_CONTINUOUS_GRABBING]):
            pass

        elif(msg.msg_type == t.ERROR):
            if(Message.ERROR_CODE_ATTR_NAME not in kwargs):
                raise ValueError(
                    f"Parameter '{Message.ERROR_CODE_ATTR_NAME}'	 must be given for message with type {msg.msg_type}")
            setattr(msg, Message.ERROR_CODE_ATTR_NAME,
                    kwargs[Message.ERROR_CODE_ATTR_NAME])
            payload_content += struct.pack(">B",
                                           getattr(msg,
                                                   Message.ERROR_CODE_ATTR_NAME))

        elif(msg.msg_type == t.CAMERA_LIST):
            if(Message.XML_CAMERA_LIST_ATTR_NAME not in kwargs):
                raise ValueError(
                    f"Parameter '{Message.XML_CAMERA_LIST_ATTR_NAME}' must be given for message with type {msg.msg_type}")
            xml = kwargs[Message.XML_CAMERA_LIST_ATTR_NAME]
            setattr(msg, Message.XML_CAMERA_LIST_ATTR_NAME, xml)
            xml_encoded = xml.encode('ASCII')
            payload_content += struct.pack(
                f">{len(xml_encoded)}s", xml_encoded)

        elif(msg.msg_type == t.OPEN_CAMERA):
            if(Message.CAMERA_SERIAL_NUMBER_ATTR_NAME not in kwargs):
                raise ValueError(
                    f"Parameter '{Message.CAMERA_SERIAL_NUMBER_ATTR_NAME}' must be given for message with type {msg.msg_type}")
            serial_number = kwargs[Message.CAMERA_SERIAL_NUMBER_ATTR_NAME]
            setattr(msg, Message.CAMERA_SERIAL_NUMBER_ATTR_NAME, serial_number)
            serial_number_encoded = serial_number.encode('ASCII')
            payload_content += struct.pack(
                f">{len(serial_number_encoded)}s",
                serial_number_encoded)

        elif(msg.msg_type in [t.FRAME, t.ACK_CONTINUOUS_GRABBING]):
            if(msg.msg_type in [t.FRAME, t.ACK_CONTINUOUS_GRABBING]):
                if(Message.FRAME_NUMBER_ATTR_NAME not in kwargs):
                    raise ValueError(
                        f"Parameter '{Message.FRAME_NUMBER_ATTR_NAME}' must be given for message with type {msg.msg_type}")
                setattr(msg, Message.FRAME_NUMBER_ATTR_NAME,
                        kwargs[Message.FRAME_NUMBER_ATTR_NAME])
                payload_content += struct.pack(f">I",
                                               kwargs[Message.FRAME_NUMBER_ATTR_NAME])

            if(msg.msg_type == t.FRAME):
                if(Message.FRAME_TIMESTAMP_ATTR_NAME not in kwargs):
                    raise ValueError(
                        f"Parameter '{Message.FRAME_TIMESTAMP_ATTR_NAME}' must be given for message with type {msg.msg_type}")
                setattr(msg, Message.FRAME_TIMESTAMP_ATTR_NAME,
                        kwargs[Message.FRAME_TIMESTAMP_ATTR_NAME])
                payload_content += struct.pack(f">Q",
                                               kwargs[Message.FRAME_TIMESTAMP_ATTR_NAME])

                if(Message.FRAME_ATTR_NAME not in kwargs):
                    raise ValueError(
                        f"Parameter '{Message.FRAME_ATTR_NAME}' must be given for message with type {msg.msg_type}")

                frame = kwargs[Message.FRAME_ATTR_NAME]
                if(not isinstance(frame, np.ndarray) or frame.ndim != 2 or frame.dtype != np.float32):
                    raise ValueError(
                        f"Parameter '{Message.FRAME_ATTR_NAME}' must be a numpy array with dimension 2 and dtype np.float32")
                setattr(msg, Message.FRAME_ATTR_NAME,
                        kwargs[Message.FRAME_ATTR_NAME])

                frame_height, frame_width = frame.shape
                payload_content += struct.pack(f">HH",
                                               frame_height, frame_width)
                payload_content += struct.pack(
                    f">{frame_height*frame_width}f", *frame.flatten())

        else:
            raise ValueError(f"Unknown message type {msg.msg_type}")

        msg.__buffer += struct.pack(f">I", len(payload_content))
        msg.__buffer += struct.pack(f">{len(payload_content)}B",
                                    *payload_content)
        return msg

    @staticmethod
    def xml_to_camera_list(connector, xml):
        '''
        Static method that convert XML received in CAMERA_LIST message to the list of instances of cameras.
        `ValueError exception <https://docs.python.org/3/library/exceptions.html#ValueError>`_  is raised when XML is not valid according to WRP.

        **Params**

        * connector: WRPConnector that will be used by the camera to communicate with the server
        * xml: str, received from the socket

        **Return**

        list of instances of :class:`Camera`
        '''
        try:
            root = ET.fromstring(xml)
        except ET.ParseError:
            raise ValueError("Received XML could not be parsed")

        if(root.tag != "Cameras"):
            raise ValueError(
                "Received XML does not have root element 'Cameras'")

        camera_list = []
        for camera_el in root:
            if(camera_el.tag != "Camera"):
                raise ValueError(
                    f"Received XML contains unknown element {camera_el.tag} (expected was 'Camera')")

            camera_instance = Camera(connector)
            for key, (attr_name, attr_dtype) in Camera.ATTRIBUTES.items():
                try:
                    attr_value = camera_el.attrib[key]
                except KeyError:
                    raise ValueError(
                        f"Received XML does not contain mandatory attribute {key} for element {camera_el.tag}")

                try:
                    attr_value = attr_dtype(attr_value)
                except ValueError:
                    raise ValueError(
                        f"Attribute {key} for element {camera_el.tag} could not be converted to datatype {attr_dtype}")

                setattr(camera_instance, attr_name, attr_value)

            camera_list.append(camera_instance)

        return camera_list
