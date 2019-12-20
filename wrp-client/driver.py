from message import Message
import asyncio

class Driver:
    '''
    TODO add docstring
    '''
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
        data = await self.__reader.read()
        return Message.create_message(buffer=data)
    

