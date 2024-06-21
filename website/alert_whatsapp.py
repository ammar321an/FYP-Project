import sys
from twilio.rest import Client

# Get the user's email and contact number from command-line arguments
user_email = sys.argv[1]
user_contact_number = sys.argv[2]

# Ensure the contact number is in the correct format
if not user_contact_number.startswith('+'):
    user_contact_number = '+6' + user_contact_number.replace(' ', '')

# Your Twilio account SID and Auth Token
account_sid = '' #ssid
auth_token = '' #Auth token
client = Client(account_sid, auth_token)

# Your Twilio sandbox WhatsApp number
twilio_whatsapp_number = '' #Put here

# Message details
subject = "*Alert:*"
message_body = "Monkey Detected! Please check the garden immediately."

# Ensure the contact number is in the correct format
recipient_whatsapp_number = 'whatsapp:' + user_contact_number.replace(' ', '')

# Send the message
message = client.messages.create(
    body=f"{subject}\n{message_body}",
    from_=twilio_whatsapp_number,
    to=recipient_whatsapp_number
)
print(message.sid)
