import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd

# Email server configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = 'yamini582006@gmail.com'
SENDER_PASSWORD = 'qemg fgtb lxzz ixbg'

# Base URL for phishing links (replace with local Flask server IP)
TRACKING_URL = 'https://533b-2401-4900-2310-c68a-e9c3-692-8f67-3d91.ngrok-free.app/track-click?email='

# Read recipient list from CSV
recipients = pd.read_csv('email_list.csv')

def send_emails():
    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)

        # Loop through each recipient
        for _, row in recipients.iterrows():
            redirecting = '&redirect=https://aakashkumar-2005.github.io/phising_awareness_CEO/'
            recipient_email = row['Email']
            tracking_link = TRACKING_URL + recipient_email + redirecting

            # Create the email content
            subject = "Exclusive Employee Benefits Program: Company Expansion Initiative"
            body = f"""
            Dear Employee,

            As a part of the company Outside India, We are excited to introduce an exclusive Employee Benefits Program. This initiative aims to enhance employee satisfaction and reward your contribution to TVS Mobility's success.

            To enroll and activate your benefits, Please visit the following link:
            {tracking_link}

            Enrollment is open until [Insert Deadline]. Don't miss this oppurtunity to be part of this exciting new initiative!

            Thank you for your dedication and hard work.

            Best regards,  
            [CEO Name]  
            Chief Executive Officer  
            TVS Mobility
            """

            # Create the MIME message
            msg = MIMEMultipart()
            msg['From'] = SENDER_EMAIL
            msg['To'] = recipient_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            # Send the email
            server.send_message(msg)
            print(f"Email sent to {recipient_email}")

        # Close the server
        server.quit()
        print("All emails sent successfully.")

    except Exception as e:
        print(f"Error: {e}")


# Send the emails
send_emails()


#python emailsend.py  command to run this ..
# for tracking url , the command is " ngrok http 5000"