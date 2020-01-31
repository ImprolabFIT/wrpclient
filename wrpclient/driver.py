import struct
import asyncio
from .message import Message


class Driver:
    __reader = None
    __writer = None
    __event_loop = None

    def __init__(self):
        self.__event_loop = asyncio.get_event_loop()

    async def connect(self, ip_address, port):
        self.__reader, self.__writer = await asyncio.open_connection(ip_address, port)

    async def disconnect(self):
        self.__writer.close()
        await self.__writer.wait_closed()
        self.__writer = None
        self.__reader = None

    async def send_message(self, message):
        self.__writer.write(message.encode())
        await self.__writer.drain()

    async def receive_message(self):
        message_type_value, payload_length = struct.unpack(">BI", await self.__reader.readexactly(Message.MESSAGE_TYPE_LENGTH + Message.PAYLOAD_SIZE_LENGTH))
        if(payload_length > 0):
            payload = await self.__reader.readexactly(payload_length)
        else:
            payload = bytes()
        response = Message.create_message_from_buffer(
            message_type_value=message_type_value,
            payload=payload,
            payload_length=payload_length)
        return response
