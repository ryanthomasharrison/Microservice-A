import base64
import logging
import smtplib
import zmq
from dataclasses import dataclass
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.text import MIMEText
from signal import signal, SIGINT, SIG_DFL

default_email = "cs361.group55@gmail.com"
default_password = "rddv jysq efqu wvaf"


@dataclass
class EmailPayload:
    sender_email: str
    sender_password: str
    receiver_email: str
    data: str
    data_type: str
    subject: str

    def __post_init__(self):
        # Use default email/password if not provided by client in payload
        if self.sender_email is None or self.sender_password is None:
            self.sender_email = default_email
            self.sender_password = default_password

        # Decode base64 if an image was provided
        if self.data_type == "image":
            self.data = base64.b64decode(self.data)


# Set up error log
logging.basicConfig(
    filename="error.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def send_email(ep: EmailPayload):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(ep.sender_email, ep.sender_password)

        mime_email = MIMEMultipart()
        mime_email["From"] = ep.sender_email
        mime_email["To"] = ep.receiver_email
        mime_email["Subject"] = ep.subject

        if ep.data_type == "image":
            mime_attachment = MIMEImage(ep.data)
        elif ep.data_type == "text":
            mime_attachment = MIMEText(ep.data)
        else:
            raise ValueError("Only text or image file types are supported")

        mime_attachment.add_header("Content-Disposition", "attachment")
        mime_email.attach(mime_attachment)
        server.sendmail(ep.sender_email, ep.receiver_email, mime_email.as_string())

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

# exit if user sends SIGINT or ctrl+c
signal(SIGINT, SIG_DFL)

# Wait for client request
while True:
    print("Listening on ", address)

    # Prepare response JSON
    response = {"success": None, "message": None, "error": None}

    try:
        json_payload = socket.recv_json()
        ep = EmailPayload(**json_payload)

        # Send email
        send_email(ep)

        # Update JSON response
        response["success"] = True
        response["message"] = (
            f"Email containing {ep.data_type.upper()} with subject '{ep.subject}"
            f" has been sent to {ep.receiver_email}"
        )

    except Exception as error:
        # Update JSON response
        logging.error("Error occurred while processing client request: %s", error)
        response["success"] = False
        response["message"] = "Error occurred while sending. Email not sent."
        response["error"] = f"{type(error).__name__}:\t{str(error)}"

    # Send response back to client
    socket.send_json(response)
