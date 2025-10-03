import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Email credentials
sender_email = "syedali233d@gmail.com"
receiver_email = "syedali233d@gmail.com"
password = "cvfl hhuh uxoo ufgl"  # Use an App Password, not your Gmail password

# Create the email
message = MIMEMultipart()
message["From"] = sender_email
message["To"] = receiver_email
message["Subject"] = "Test Email from Python"

# Email body
body = "Hello, this is a test email sent from Python!"
message.attach(MIMEText(body, "plain"))

# Connect to Gmail SMTP server
try:
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()  # Upgrade the connection to secure
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message.as_string())
    print("✅ Email sent successfully!")
except Exception as e:
    print("❌ Error:", e)
finally:
    server.quit()
