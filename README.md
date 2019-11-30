# Remote server-client connector for WIC SDK

Client part of the unofficial remote connector for Thermal cameras by Workswell. 

## Motivation

We would like to connect to [Thermal cameras by Workswell](https://workswell.cz/termokamera-workswell-infrared-camera-wic/) with Python, preferably from the Jupyter notebook, for the [BI&#x2011;SVZ class](https://github.com/ImprolabFIT/BI-SVZ-coursework). Problem is that Workswell provides and supports access to the cameras only through their C# SDK. Solution is to write a server-client connector. Server part of the application will be running on Windows with installed C# SDK and connected cameras to the same subnetwork. Client, implemented in this repository, is written in Python and thus is independent on the operating system. 

## Instalation

```pip install wrp-client```

## Usage

```
from datetime import datetime
from wrp_client import Client, Camera
import asyncio

client = Client()
client.connect(ip_adress="214.178.132.14", port=8412, timeout=60)

# get list of instances of Camera class
cameras = client.get_cameras()

# find specific camera
try:
	my_camera = [c for c in cameras if c.serial_number == "ABCDEF"][0]
except IndexError:
	raise CameraNotFound()

my_camera.open(timeout="20")

# Return frame (numpy matrix) filled with raw data with shape (my_camera.height, my_camera.width)
frame = my_camera.get_frame(timeout="20")

def callback(frame):
	time_str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
	frame_color = cv2.applyColorMap(frame, cv2.COLORMAP_JET)
	cv2.imwrite(f"frame-{time_str}.jpg", frame_color)

# Return frame (numpy matrix) filled with raw data with shape (my_camera.height, my_camera.width)
my_camera.start_continuous_shot(callback)

# Wait some time to collect images
asyncio.sleep(5)

my_camera.stop_continuous_shot(callback)
```

## Implementation

There are 2 classes accessible to the user (Client, Camera) and three hidden classes (Driver, WRPConnector and Message).
Their description is:

1. *Client* was given a IP address and port of the WRP server. Is able to connect and get list of cameras connected to the server.  
2. *Camera* represents Thermal camera by Workswell. Provides information about camera device, e.g. model name, serial number, maximal width and height of provided frame etc. Each camera has its own instance of WRPConnector and can through it call function like `get_frame` or `start_continuous_shot`. 
3. *WRPConnector* works like a finite state machine and implements logic of the application protocol WRP. 
2. *Message* is a structure handy for passing all the informations about the message together. Contains dynamic attributes according to the type of message and is able to serialize itself according to WRP.  
3. *Driver* keeps connection (socket) with the server and is responsible for asynchronous sending and receiving messages on the order of the WRPConnector.


## Notes for MI-PYT semestral work

If you think that this project is not enough ambitious for the MI-PYT semestral work (although to write state finite machine using asyncio seems challenging to me), I could implement some of these extensions:

1. More advanced usage, where timeouts are not used in functions `open`, `get_frame` etc., but these methods are asynchronous as well and are used in cooperation with the asyncio library. 

2. Inner methods of *Driver*, *Message* and *WRPConnector* classes could be implemented in Cython to provide sufficient speed. This could be handy because these methods will be called 30 times (or more) a second to process each frame.

3. GUI where you can fill IP address of the server, select camera and watch the stream of frames. But that would probably be better as an independent project that only uses this client, because what most of the users (at least BI-SVZ students) want is an API to get the frame, which they can process.

4. Command Line Interface, that provides reasonable scenarios, e.g. connect to IP address XXX.XXX.XXX.XXX, take Y frames and save them to files ZZZ_1.png, ..., ZZZ_Y.png.

#### Workswell Remote Protocol (WRP)

Here goes the definition and description of the WRP protocol. 



