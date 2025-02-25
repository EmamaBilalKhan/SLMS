import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import random
from redis import Redis

redis_client = Redis(host="localhost", port=6379, db=0, decode_responses=True)

def send_verification_email(to,id):
    try:
        SENDER_EMAIL = os.environ.get("MAIL_FROM")
        SENDER_PASSWORD = os.environ.get("MAIL_PASSWORD")
        verification_code = random.randint(100000, 999999)
        redis_client.setex(name=id, time=240, value=verification_code)
        subject = "SLMS Verification Code"
        body = f"Your One-time verification code for SLMS is: {verification_code}. It expires in 4 minutes."
        msg = MIMEMultipart()
        msg["From"] = SENDER_EMAIL
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(SENDER_EMAIL, SENDER_PASSWORD)
        s.sendmail(os.environ.get("MAIL_FROM"), to, msg=msg.as_string())
        s.quit()
    except Exception as e:
        return {"error": str(e)}

def verify_email_code(user_id, code):
    try:
        verification_code = redis_client.get(name=user_id)
        if verification_code == code:
            return True
        else:
            return False
    except Exception as e:
        return {"error": str(e)}