import smtplib
from email.mime.text import MIMEText
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# Load from environment or fallback
GMAIL_USER = os.getenv("GMAIL_USER", "")
GMAIL_PASS = os.getenv("GMAIL_PASS", "")
TO_EMAIL = os.getenv("NOTIFY_EMAIL", "")


def send_email(subject: str, body: str):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = TO_EMAIL

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_PASS)
            server.sendmail(GMAIL_USER, TO_EMAIL, msg.as_string())
        print("✅ Email sent")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: send_email.py <subject> <body>")
        sys.exit(1)
    send_email(sys.argv[1], sys.argv[2])
