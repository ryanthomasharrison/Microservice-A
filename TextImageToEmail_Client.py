import base64
import json

def CreateJSONtoSend(data, email):
    # If data to send is text
    if isinstance(data, str):
        data_to_send = data
        data_type = "text"
    # Else if data to send is an image
    else:
        data_to_send = base64.b64encode(data).decode('utf-8')
        data_type = "image"

    # Create JSON payload
    payload = {"data": data_to_send, 
               "dataType": data_type, 
               "email": email}

    # Serialize the JSON payload
    payload_serialized = json.dumps(payload)

    return payload_serialized
