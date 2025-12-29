import json
from utils.redis_instance import redis_client
from dotenv import load_dotenv
import logging
import os
from email.message import EmailMessage
import smtplib
from utils.email_templates import signup_template

logging.basicConfig(filename="email_worker.log",
                    format='%(asctime)s %(message)s',
                    filemode='a',
                    level=logging.INFO)
load_dotenv()

QUEUE_NAME="queue:email"
SENDER_EMAIL = os.getenv("EMAIL_ADDRESS")
SENDER_PASS = os.getenv("EMAIL_PASSWORD")

def send_email(subject: str, body: str, to_email: str):
    try:
        sender_mail=SENDER_EMAIL
        sender_pass=SENDER_PASS
        msg=EmailMessage()

        msg['Subject']=subject
        msg['From']=sender_mail
        msg['To']=to_email
        msg.add_alternative(body, subtype="html")

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(sender_mail, sender_pass)
            smtp.send_message(msg)
        
        logging.info("Email Sent to "+to_email)
    except Exception as e:
        raise e

def process_job(job:dict):
    try:
        email_type=job['type']
        name=job['name']
        email=job['email']

        token=job['token']
        if not token:
            logging.error("Missing token in job")
            return
        if email_type.lower()=='signup':
            body=signup_template(base_url=os.getenv('CLIENT_BASE_URL'),name=name,token=token)
            send_email("Thanks for Signing Up",body,email)
    except Exception as e:
        raise e

def start_worker():
    print("Worker Started")
    logging.info("Waiting For Jobs......")

    while True:
        try:
            _,data=redis_client.blpop(QUEUE_NAME)
            job = json.loads(data)
            process_job(job)

        except Exception as e:
            logging.exception('Error while processing jobs. '+e)

if __name__ == "__main__":
    start_worker()