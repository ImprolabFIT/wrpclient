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

# find camera with specific serial number
my_camera = client.get_camera(serial_number="ABCDEF")

my_camera.open(timeout="20")

# Return frame (numpy matrix) filled with raw data with shape (my_camera.height, my_camera.width)
frame = my_camera.get_frame(timeout="20")

def callback(frame):
	time_str = datetime.now().strftime("%Y-%m-%d-%H-%M-%S-%f")
	frame_color = cv2.applyColorMap(frame, cv2.COLORMAP_JET)
	cv2.imwrite(f"frame-{time_str}.jpg", frame_color)

# Give handler for continuous shot that saves colorized images with timestamp suffix
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

State diagram of WRP is following:
<div class="mxgraph" style="max-width:100%;border:1px solid transparent;" data-mxgraph="{&quot;highlight&quot;:&quot;#0000ff&quot;,&quot;nav&quot;:true,&quot;resize&quot;:true,&quot;toolbar&quot;:&quot;zoom layers lightbox&quot;,&quot;edit&quot;:&quot;_blank&quot;,&quot;xml&quot;:&quot;&lt;mxfile host=\&quot;www.draw.io\&quot; modified=\&quot;2020-01-17T06:41:18.915Z\&quot; agent=\&quot;Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/79.0.3945.79 Chrome/79.0.3945.79 Safari/537.36\&quot; etag=\&quot;C6GbpVDrhF7r06hWTV__\&quot; version=\&quot;12.5.5\&quot; type=\&quot;google\&quot;&gt;&lt;diagram name=\&quot;Page-1\&quot; id=\&quot;c7488fd3-1785-93aa-aadb-54a6760d102a\&quot;&gt;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&lt;/diagram&gt;&lt;/mxfile&gt;&quot;}"></div>
<script type="text/javascript" src="https://www.draw.io/js/viewer.min.js"></script>

Black arrows are events trigggered by the client, red ones comes from the server.
Message is composed of header, that specifies message type, payload length and payload. 
Messages are:

|	Type						|	Type value	|	Payload size	|	Payload										|
|	----						|	-------		|	--------------	|	------- 									|
| 	INVALID						|	0			|	0				|	-											|
|	OK							|	1			|	0				|	-											|
|	ERROR						|	2			|	1				|	Error code									|
|	GET_CAMERA_LIST				|	3			|	0				|	-											|
|	CAMERA_LIST					|	4			|	variable		|	XML with listed cameras						|
|	OPEN_CAMERA					|	5			|	variable		|	Serial no. of camera						|
|	CLOSE_CAMERA				|	6			|	0				|	-											|
|	GET_FRAME					|	7			|	0				|	-											|
|	FRAME						|	8			|	variable		|	Frame no., Timestamp, Height, Width, Frame	|
|	START_CONTINUOUS_GRABBING	|	9			|	0				|	-											|
|	STOP_CONTINUOUS_GRABBING	|	10			|	0				|	-											|
|	ACK_CONTINUOUS_GRABBING		|	11			|	5				|	Frame no. 									|	

Payload content datatypes:

|	Name						|	Datatype				|
|	----						|	-------					|
|	Error code					|	uint8					|
|	XML with listed cameras		|	string					|
|	Serial no. of cameras		|	string					|
|	Camera ID					|	uint8					|
|	Frame no.					|	uint32					|
|	Timestamp					|	uint64					|
|	Height						|	uint16					|
|	Width						|	uint16					|
|	Frame						|	array of 32-bit float	|

Error codes are:

|	Code					|	Code value	|
|	----					|	---------	|
|	UNEXPECTED_MESSAGE		|	0			|
|	CAMERA_NOT_FOUND		|	1			|
|	CAMERA_NOT_RESPONDING	|	2			|
|	CAMERA_NOT_OPEN			|	3			|
|	CAMERA_NOT_CONNECTED	|	4			|
|	CAMERA_NOT_ACQUIRING	|	5			|
