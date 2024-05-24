import base64
import json
import zmq
from signal import signal, SIGINT, SIG_DFL

test_email_target = "ryanharrison.cs361@gmail.com"


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


def CreateJSONtoSend(
    data, data_type, subject, receiver_email, sender_email=None, sender_password=None
):
    # If data to send is text
    if isinstance(data, str):
        data_to_send = data
        data_type = "text"
    # Else if data to send is an image
    elif isinstance(data, bytes):
        data_to_send = base64.b64encode(data).decode("utf-8")
        data_type = "image"
    else:
        raise ValueError("Only text or image file types are supported")

    # Create JSON payload
    payload = {
        "data": data_to_send,
        "data_type": data_type,
        "subject": subject,
        "receiver_email": receiver_email,
        "sender_email": sender_email,
        "sender_password": sender_password,
    }

    # Serialize the JSON payload
    payload_serialized = json.dumps(payload)

    return payload_serialized


def send_data_to_microservice(json_payload):
    try:
        # Set up socket
        context = zmq.Context()
        socket = context.socket(zmq.REQ)
        socket.connect("tcp://localhost:5555")

        # exit if user sends SIGINT or ctrl+c
        signal(SIGINT, SIG_DFL)

        # Send data to microservice
        socket.send(json_payload.encode("utf-8"))

        # Receive response
        response = json.loads(socket.recv().decode("utf-8"))
        socket.close()

        # Print response
        for key, value in response.items():
            print(f"{key}: {value}")

    except Exception as error:
        print("Error: ", error)


"""
TESTING PROGRAM
"""

# Testing CreateJSONtoSend function
sample_text = read_file("Sample_data/SampleText.txt", "text")

sample_image = read_file("Sample_data/SampleImage.png", "image")

print("Sending email")

# Convert text to JSON
text_JSON = CreateJSONtoSend(
    sample_text, "text", "test email - text", test_email_target
)

# # Convert image to JSON
image_JSON = CreateJSONtoSend(
    sample_image, "image", "test email - image", test_email_target
)

error_test = "this is not a JSON file"

# Send JSON to microservice
# send_data_to_microservice(text_JSON)  # Text
# send_data_to_microservice(image_JSON) # Image
# send_data_to_microservice(error_test) # Error
