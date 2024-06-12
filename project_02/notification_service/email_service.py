import smtplib
import ssl
import os
import json
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()


def notification(message):
    try:
        message = json.loads(message)
        receiver_address = message["email"]
        subject = message["subject"]
        body = message["body"]

        # Retrieve email credentials from environment variables
        sender_address = os.environ.get("MAIL_ADDRESS")
        sender_password = os.environ.get("MAIL_PASSWORD")

        # Gmail SMTP server settings
        smtp_server = 'smtpout.secureserver.net'
        smtp_port = 465

        # Create a secure SSL context and connect to the server
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, smtp_port, context=context) as server:
            server.login(sender_address, sender_password)

            # Compose the email message
            msg = MIMEText(body)
            msg['Subject'] = subject
            msg['From'] = sender_address
            msg['To'] = receiver_address

            # Send the email
            server.sendmail(sender_address, receiver_address, msg.as_string())

        print("Mail Sent")
    except Exception as e:
        print(f"Failed to send email: {e}")
