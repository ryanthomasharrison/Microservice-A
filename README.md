# Text/Image to Email Microservice
## Overview
Allows a client program to send a text file or an image file to a specified email address
## How to Request Data from Microservice
The client program needs to provide a serialized JSON payload containing the following information
1) **Data:** text (string) or image (encodeded in base64)
3) **Data type** (string)
4) **Receiver email** (string)
5) **Email subject** (string)
6) *optional* **Sender email** (string) 
7) *optional* **Sender passsword** (string)

Using a zeroMQ socket, the client program sends the JSON payload to the microservice and waits for a response

### Set up zeroMQ socket
`context = zmq.Context()`\
`socket = context.socket(zmq.REQ)`\
`socket.connect("tcp://localhost:5555")`

### Example Call to Microservice

`# Convert image to serialized JSON with encoded base64 image`\
`image_JSON = CreateJSONtoSend(sample_image, "image", "test email - image", "ryanharrison.cs361@gmail.com")`

`# Send serialized JSON to microservice`\
`send_data_to_microservice(image_JSON)`

## How to Receive Data from Microservice
Once email has been sent in the microservice, a JSON response is sent back to the client program that provides:
- Whether email was sent successfully
- Summary message that will indicate what was sent and to whom if email is successful
- Any errors that occurred

### Receiving a response
ZeroMQ socket receives the JSON response from microservice and decodes it

`response = json.loads(socket.recv().decode("utf-8"))`

### After response is received
Client program can print the response

#### Successful response example
`success: True`\
`message: Email containing IMAGE with subject 'test email - image' has been sent to ryanharrison.cs361@gmail.com`\
`error: None`

#### Unsuccessful response example
`success: False`\
`message: Error occurred while sending. Email not sent.`\
`error: JSONDecodeError: Expecting value: line 1 column 1 (char 0)`

## UML Diagram

![TextImagetoEmail_Microservice drawio](https://github.com/ryanharrison89/Microservice-A/assets/101477154/85adfbc0-124a-4d35-92b0-071a8b56f02c)

