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
<div class="mxgraph" style="max-width:100%;border:1px solid transparent;" data-mxgraph="{&quot;highlight&quot;:&quot;#0000ff&quot;,&quot;nav&quot;:true,&quot;resize&quot;:true,&quot;toolbar&quot;:&quot;zoom layers lightbox&quot;,&quot;edit&quot;:&quot;_blank&quot;,&quot;xml&quot;:&quot;&lt;mxfile host=\&quot;www.draw.io\&quot; modified=\&quot;2019-12-25T11:24:43.717Z\&quot; agent=\&quot;Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36\&quot; etag=\&quot;aOXY62vzwFa9mMSJ6glI\&quot; version=\&quot;12.4.3\&quot; type=\&quot;google\&quot; pages=\&quot;1\&quot;&gt;&lt;diagram name=\&quot;Page-1\&quot; id=\&quot;c7488fd3-1785-93aa-aadb-54a6760d102a\&quot;&gt;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&lt;/diagram&gt;&lt;/mxfile&gt;&quot;}"></div>
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

|	Code				|	Code value	|	Description	|
|	----				|	---------	|	-----------	|
|	UNEXPECTED_MESSAGE	|	0			|	TODO		|
|	CAMERA_DISCONNECTED	|	1			|	TODO		|
|	WRONG_CAMERA_ID		|	2			|	TODO		|

	
