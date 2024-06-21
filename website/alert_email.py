import sys
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Get the user's email from command-line arguments
user_email = sys.argv[1]

# Email configuration
sender_email = "" #Put the sender email here
sender_password = ""  # This should be an "app" password if using Gmail.
smtp_server = "smtp.gmail.com"
smtp_port = 587

# Create the email message
message = MIMEMultipart("alternative")
message["Subject"] = "Intrusion Alert Notification: Monkey Detected!"
message["From"] = sender_email
message["To"] = user_email

# Create the plain-text and HTML version of your message
text = """\
Alert:
Monkey Detected! Please check the garden immediately."""

html = """\
<html>
  <body>
    <p><strong>Alert:</strong><br>
       Monkey Detected! Please check the garden immediately.
    </p>
  </body>
</html>
"""

# Turn these into plain/html MIMEText objects
part1 = MIMEText(text, "plain")
part2 = MIMEText(html, "html")

# Add HTML/plain-text parts to MIMEMultipart message
# The email client will try to render the last part first
message.attach(part1)
message.attach(part2)

# Send the email
try:
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()  # Secure the connection
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, user_email, message.as_string())
    print(f"Email has been sent to {user_email}")
except Exception as e:
    print(f"Error sending email: {e}")
finally:
    server.quit()
