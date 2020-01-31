from wrpclient import Client
from wrpserver import WRPServer
import pytest
import numpy as np
import asyncio

@pytest.fixture
async def wrp_server():
	server = WRPServer()
	await server.run()
	yield server
	await server.stop()
	del server

def fake_and_real_camera_matches(fake_server_camera, client_camera):
	assert fake_server_camera.SerialNumber == client_camera.serial_number
	assert fake_server_camera.ModelName == client_camera.model_name
	assert fake_server_camera.Width == client_camera.width
	assert fake_server_camera.Height == client_camera.height
	assert fake_server_camera.CameraMaxFPS == client_camera.camera_max_fps
	assert fake_server_camera.Version == client_camera.version
	assert fake_server_camera.ManufacturerInfo == client_camera.manufacturer_info
	assert fake_server_camera.VendorName == client_camera.vendor_name

#===============================================================
# Testing asynchronous versions of methods
#===============================================================
@pytest.mark.asyncio
async def test_connect_async(wrp_server):
	client = Client()
	assert client.is_connected() == False
	await client.connect_async(ip_address=WRPServer.SERVER_IP_ADDRESS, port=WRPServer.DEFAULT_PORT)
	assert client.is_connected() == True
	await client.disconnect_async()
	assert client.is_connected() == False

@pytest.mark.asyncio
@pytest.mark.parametrize('port_change', (-10, -5, -2, -1, 1, 2, 5, 10))
async def test_connect_wrong_port_async(wrp_server, port_change):
	client = Client()
	with pytest.raises(ConnectionRefusedError):
		await client.connect_async(ip_address=WRPServer.SERVER_IP_ADDRESS, port=WRPServer.DEFAULT_PORT+port_change)

@pytest.mark.asyncio
@pytest.mark.parametrize('repeat', (1, ))#, 5, 10, 100))
@pytest.mark.parametrize('cameras_cnt', (1, ))#, 2, 5, 10, 100))
async def test_get_cameras_async(wrp_server, repeat, cameras_cnt):
	client = Client()
	await client.connect_async(ip_address=WRPServer.SERVER_IP_ADDRESS, port=WRPServer.DEFAULT_PORT)
	for i in range(repeat):
		camera_list_server = WRPServer.generate_random_valid_camera_list(cameras_cnt)
		wrp_server.camera_list = camera_list_server 
		camera_list_client = await client.get_cameras_async()
		assert len(camera_list_client) == len(camera_list_server)
		for client_camera, server_camera in zip(camera_list_client, camera_list_server):
			fake_and_real_camera_matches(server_camera, client_camera)
	await client.disconnect_async()

@pytest.mark.asyncio
@pytest.mark.parametrize('serial_number', ("AAABBBCCCDDD", "1234567890", "A1B2C3D4E6F6G7H8I9J0"))
async def test_get_camera_async(wrp_server, serial_number):
	client = Client()
	await client.connect_async(ip_address=WRPServer.SERVER_IP_ADDRESS, port=WRPServer.DEFAULT_PORT)
	camera_list_server = WRPServer.generate_random_valid_camera_list(100)
	camera_list_server[0].SerialNumber = serial_number
	wrp_server.camera_list = camera_list_server 
	client_camera = await client.get_camera_async(serial_number)
	fake_and_real_camera_matches(camera_list_server[0], client_camera)
	await client.disconnect_async()


@pytest.mark.asyncio
async def test_open_and_close_async(wrp_server):
	client = Client()
	await client.connect_async(ip_address=WRPServer.SERVER_IP_ADDRESS, port=WRPServer.DEFAULT_PORT)
	camera_list_server = WRPServer.generate_random_valid_camera_list(100)
	wrp_server.camera_list = camera_list_server 
	cameras = await client.get_cameras_async()
	for camera in cameras:
		await camera.open_async()
		await camera.close_async()
	await client.disconnect_async()

@pytest.mark.asyncio
async def test_get_frame_async(wrp_server):
	client = Client()
	await client.connect_async(ip_address=WRPServer.SERVER_IP_ADDRESS, port=WRPServer.DEFAULT_PORT)
	camera_list_server = WRPServer.generate_random_valid_camera_list(20)
	wrp_server.camera_list = camera_list_server
	cameras = await client.get_cameras_async()
	for camera in cameras:
		await camera.open_async()
		for i in range(np.random.randint(0, 100)):
			frame_dict = WRPServer.generate_random_frame(camera)
			wrp_server.frame_dict = frame_dict
			server_frame = frame_dict['frame']
			server_frame_timestamp = frame_dict['frame_timestamp']
			client_frame, client_frame_timestamp = await camera.get_frame_async()
			assert np.array_equal(client_frame, server_frame)
			assert client_frame_timestamp == server_frame_timestamp
		await camera.close_async()
	await client.disconnect_async()

