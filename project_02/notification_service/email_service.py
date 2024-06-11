import smtplib, ssl
import os
import json
from email.message import EmailMessage
from dotenv import load_dotenv
from email.mime.text import MIMEText


load_dotenv()


def notification(message):
    try:
        message = json.loads(message)
        receiver_address = message["email"]
        subject = message["subject"]
        body = message["body"]
        other = message["other"]

        # Retrieve email credentials from environment variables
        sender_address = os.environ.get("GMAIL_ADDRESS")
        sender_password = os.environ.get("MAIL_PASSWORD")

        # Gmail SMTP server settings
        smtp_server = 'smtpout.secureserver.net'
        # Create a secure SSL context
        context = ssl.create_default_context()
        smtp_port = 465

        # Create a secure SSL context
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls(context=context)
        server.login(sender_address, sender_password)

        # Compose the email message
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = sender_address
        msg['To'] = receiver_address

        # Send the email
        server.sendmail(sender_address, receiver_address, msg.as_string())
        server.quit()

        print("Mail Sent")
    except Exception as e:
        print(f"Failed to send email: {e}")
