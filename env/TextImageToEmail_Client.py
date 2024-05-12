import base64
import json
import zmq

def read_file(file_path, file_type):
    # If file is text
    if file_type == "text":
        with open(file_path, "r") as file:
            data = file.read()
    elif file_type == "image":
        with open(file_path, "rb") as file:
            data = file.read()
    else:
        raise ValueError("Only text or image file types are supported")
    return data

def CreateJSONtoSend(data, email):
    # If data to send is text
    if isinstance(data, str):
        data_to_send = data
        data_type = "text"
    # Else if data to send is an image
    elif isinstance(data, bytes):
        data_to_send = base64.b64encode(data).decode('utf-8')
        data_type = "image"
    else:
        raise ValueError("Only text or image file types are supported")

    # Create JSON payload
    payload = {"data": data_to_send, 
               "dataType": data_type, 
               "email": email}

    # Serialize the JSON payload
    payload_serialized = json.dumps(payload)

    return payload_serialized

def send_data_to_microservice(json_payload):
    try:
        # Set up socket and send data to microservice
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tsp://localhost:5555")
        socket.send(json_payload.encode("utf-8"))
        response = json.loads(socket.recv().decode("uft-8"))
        socket.close()

        # Tell client program whether email was sent successfully or not
        if response["success"]:
            print("Success! Email was sent")
        else:
            print("Error - email did not send. Error message: ", response["error"])

    except Exception as error:
        print("Error: ", error)




"""
TESTING PROGRAM
"""

# Testing CreateJSONtoSend function
sample_text = read_file("Sample_data/SampleText.txt", "text")

sample_image = read_file("Sample_data/SampleImage.png", "image")

# Convert text to JSON
text_JSON = CreateJSONtoSend(sample_text, "test@test.com")

# Convert image to JSON
image_JSON = CreateJSONtoSend(sample_image, "test@test.com")

print(text_JSON)

