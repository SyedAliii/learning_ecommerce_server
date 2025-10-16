from email.message import EmailMessage
import aiosmtplib
import asyncio
from app.core.celery_worker import celery
from app.core.config import settings

@celery.task
def send_email_task(to_email: str, subject: str, body: str):
    asyncio.run(send_email_async(to_email, subject, body))

async def send_email_async(to_email: str, subject: str, body: str):
    sender_email = settings.SENDER_EMAIL
    sender_password = settings.APP_PASSWORD
    smtp_server = settings.SMTP_SERVER
    smtp_port = settings.SMTP_PORT

    message = EmailMessage()
    message["From"] = sender_email
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    try:
        await aiosmtplib.send(
            message,
            hostname=smtp_server,
            port=smtp_port,
            start_tls=True,
            username=sender_email,
            password=sender_password,
        )
        print(f"Email sent to {to_email}")
    except Exception as e:
        print(f"Failed to send email: {e}")

# @celery.task
# def send_email_task(to_email: str, subject: str, body: str):
#     import asyncio
#     loop = asyncio.get_event_loop()
#     if loop.is_running():
#         # already in event loop (rare for Celery)
#         asyncio.create_task(send_email_async(to_email, subject, body))
#     else:
#         loop.run_until_complete(send_email_async(to_email, subject, body))
