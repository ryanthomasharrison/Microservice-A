import base64
import json
import zmq
import smtplib
import email.mime


def send_email(sender_email, sender_password, recipient_email, email_subject, email_data, data_type):
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)

        mime_email = email.mime.multipart.MIMEMultipart()
        mime_email["From"] = sender_email
        mime_email["To"] = recipient_email
        mime_email["Subject"] = email_subject

        if data_type == "image":
            mime_attachment = email.mime.image.MIMEImage(email_data)
        elif data_type == "text":
            mime_attachment = email.mime.text.MIMEText(email_data)
        else:
            raise ValueError("Only text or image file types are supported")

        mime_attachment.add_header("Content-Disposition", "attachment")
        mime_email.attach(mime_attachment)
        server.sendmail(sender_email, recipient_email, mime_email.as_string())

        return f"Success! Email has been sent to {recipient_email}"
    
    except Exception as error:
        print(f"Error in sending: {error}")
        return str(error)
    
    finally:
        server.quit()


# Set up and bind socket
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

# Wait for client request
while True:
    json_payload = socket.recv_json()

    # Extract data from json payload
    data = json_payload["data"]
    data_type = json_payload["dataType"]
    receiver_email = json_payload["email"]
    subject = json_payload["subject"]
    
    # Get sender email and password if provided, otherwise use default email/password in function call below
    sender_email = json_payload.get("senderEmail")
    sender_password = json_payload.get("senderPassword")
    
    if sender_email is None and sender_password is None:
        sender_email = "cs361.group55@gmail.com"
        sender_password = "textimagetoemail"

    # Decode base64 if an image was provided
    if data_type == "image":
        data = base64.b64decode(data)

    # Prepare response JSON
    response = {"success": None, "message": None, "error": None}

    # Send email
    try:
        send_email(sender_email, sender_password, receiver_email, subject, data, data_type)
        
        # Update JSON response
        response["success"] = True
        response["message"] = f"Email has been sent successfully to {receiver_email}"

    except Exception as error:
        # Update JSON response
        response["success"] = False
        response["message"] = f"Error occurred while sending. Email not sent to {receiver_email}"
        response["error"] = str(error)

    # Send response back to client
    socket.send_json(response)

    




        
