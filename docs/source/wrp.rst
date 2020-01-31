.. _WRP Definition:

Workswell Remote Protocol (WRP)
-------------------------------

State diagram of WRP is following:

.. raw:: html

	<div class="mxgraph" style="max-width:100%;border:1px solid transparent;" data-mxgraph="{&quot;highlight&quot;:&quot;#0000ff&quot;,&quot;nav&quot;:true,&quot;resize&quot;:true,&quot;toolbar&quot;:&quot;zoom layers lightbox&quot;,&quot;edit&quot;:&quot;_blank&quot;,&quot;xml&quot;:&quot;&lt;mxfile host=\&quot;www.draw.io\&quot; modified=\&quot;2020-01-31T20:14:57.527Z\&quot; agent=\&quot;Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/79.0.3945.79 Chrome/79.0.3945.79 Safari/537.36\&quot; etag=\&quot;oqPbG_alXBiinnCZe2o8\&quot; version=\&quot;12.6.2\&quot; type=\&quot;google\&quot;&gt;&lt;diagram name=\&quot;Page-1\&quot; id=\&quot;c7488fd3-1785-93aa-aadb-54a6760d102a\&quot;&gt;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&lt;/diagram&gt;&lt;/mxfile&gt;&quot;}"></div>
	<script type="text/javascript" src="https://www.draw.io/js/viewer.min.js"></script>
	
Black arrows are events trigggered by the client, red ones comes from the server.
Message is composed of header, that specifies message type, payload length and payload. 
Messages are:

+-------------------------------+---------------+-------------------+-----------------------------------------------+
|    Type                       |    Type value |    Payload size   |    Payload                                    |
+===============================+===============+===================+===============================================+
|    INVALID                    |    0          |    0              |                                               |
+-------------------------------+---------------+-------------------+-----------------------------------------------+
|    OK                         |    1          |    0              |                                               |
+-------------------------------+---------------+-------------------+-----------------------------------------------+
|    ERROR                      |    2          |    1              |    Error code                                 |
+-------------------------------+---------------+-------------------+-----------------------------------------------+
|    GET_CAMERA_LIST            |    3          |    0              |                                               |
+-------------------------------+---------------+-------------------+-----------------------------------------------+
|    CAMERA_LIST                |    4          |    variable       |    XML with listed cameras                    |
+-------------------------------+---------------+-------------------+-----------------------------------------------+
|    OPEN_CAMERA                |    5          |    variable       |    Serial no. of camera                       |
+-------------------------------+---------------+-------------------+-----------------------------------------------+
|    CLOSE_CAMERA               |    6          |    0              |                                               |
+-------------------------------+---------------+-------------------+-----------------------------------------------+
|    GET_FRAME                  |    7          |    0              |                                               |
+-------------------------------+---------------+-------------------+-----------------------------------------------+
|    FRAME                      |    8          |    variable       |    Frame no., Timestamp, Height, Width, Frame |
+-------------------------------+---------------+-------------------+-----------------------------------------------+
|    START_CONTINUOUS_GRABBING  |    9          |    0              |                                               |
+-------------------------------+---------------+-------------------+-----------------------------------------------+
|    STOP_CONTINUOUS_GRABBING   |    10         |    0              |                                               |
+-------------------------------+---------------+-------------------+-----------------------------------------------+
|    ACK_CONTINUOUS_GRABBING    |    11         |    5              |    Frame no.                                  |
+-------------------------------+---------------+-------------------+-----------------------------------------------+

Payload content datatypes:

+-------------------------------+---------------------------+
|    Name                       |    Datatype               |
+===============================+===========================+
|    Error code                 |    uint8                  |
+-------------------------------+---------------------------+
|    XML with listed cameras    |    string                 |
+-------------------------------+---------------------------+
|    Serial no. of cameras      |    string                 |
+-------------------------------+---------------------------+
|    Camera ID                  |    uint8                  |
+-------------------------------+---------------------------+
|    Frame no.                  |    uint32                 |
+-------------------------------+---------------------------+
|    Timestamp                  |    uint64                 |
+-------------------------------+---------------------------+
|    Height                     |    uint16                 |
+-------------------------------+---------------------------+
|    Width                      |    uint16                 |
+-------------------------------+---------------------------+
|    Frame                      |    array of 32-bit float  |
+-------------------------------+---------------------------+

Error codes are:

+---------------------------+---------------+
|    Code                   |    Code value |
+===========================+===============+
|    UNEXPECTED_MESSAGE     |    0          |
+---------------------------+---------------+
|    CAMERA_NOT_FOUND       |    1          |
+---------------------------+---------------+
|    CAMERA_NOT_RESPONDING  |    2          |
+---------------------------+---------------+
|    CAMERA_NOT_OPEN        |    3          |
+---------------------------+---------------+
|    CAMERA_NOT_CONNECTED   |    4          |
+---------------------------+---------------+
|    CAMERA_NOT_ACQUIRING   |    5          |
+---------------------------+---------------+
