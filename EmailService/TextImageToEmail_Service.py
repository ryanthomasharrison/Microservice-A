import base64
import zmq
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
import logging

# Set up error log
logging.basicConfig(filename = "error.log", level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

def send_email(sender_email, sender_password, recipient_email, email_subject, email_data, data_type):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)

        mime_email = MIMEMultipart()
        mime_email["From"] = sender_email
        mime_email["To"] = recipient_email
        mime_email["Subject"] = email_subject

        if data_type == "image":
            mime_attachment = MIMEImage(email_data)
        elif data_type == "text":
            mime_attachment = MIMEText(email_data)
        else:
            raise ValueError("Only text or image file types are supported")

        mime_attachment.add_header("Content-Disposition", "attachment")
        mime_email.attach(mime_attachment)
        server.sendmail(sender_email, recipient_email, mime_email.as_string())
    
    except Exception as error:
        logging.error("Error occurred while sending email: %s", error)
        print(f"Error in sending: {error}")
    
    finally:
        server.quit()


# Set up and bind socket
context = zmq.Context()
socket = context.socket(zmq.REP)
address = "tcp://*:5555"
socket.bind(address)

# Wait for client request
while True:
    print("Listening on ", address)


    # Prepare response JSON
    response = {"success": None, "message": None, "error": None}

    try:
        json_payload = socket.recv_json()

        # Extract data from json payload
        sender_email = json_payload["sender_email"]
        sender_password = json_payload["sender_password"]
        data = json_payload["data"]
        data_type = json_payload["data_type"]
        receiver_email = json_payload["receiver_email"]
        subject = json_payload["subject"]
        
        # Use default email/password if not provided by client in payload
        if sender_email is None and sender_password is None:
            sender_email = "cs361.group55@gmail.com"
            sender_password = "rddv jysq efqu wvaf"

        # Decode base64 if an image was provided
        if data_type == "image":
            data = base64.b64decode(data)

        # Send email
        send_email(sender_email, sender_password, receiver_email, subject, data, data_type)
        
        # Update JSON response
        response["success"] = True
        response["message"] = f"Email containing {data_type.upper()} with subject '{subject}' has been sent to {receiver_email}"

    except Exception as error:
        # Update JSON response
        logging.error("Error occurred while processing client request: %s", error)
        response["success"] = False
        response["message"] = "Error occurred while sending. Email not sent."
        response["error"] = f"{type(error).__name__}:\t{str(error)}"

    # Send response back to client
    socket.send_json(response)

    




        
