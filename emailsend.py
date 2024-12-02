import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd

# Email server configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = 'yamini582006@gmail.com'
SENDER_PASSWORD = 'qemg fgtb lxzz ixbg'

# Base URL for phishing links (replace with your ngrok public URL)
TRACKING_URL = 'https://8823-2409-40f4-f-59b2-f5a9-9769-e495-cb32.ngrok-free.app/track-click?email='

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
            <html>
            <body>
                <p>Dear Employee,</p>

                <p>As part of the company's expansion outside India, we are excited to introduce an exclusive Employee Benefits Program. 
                This initiative aims to enhance employee satisfaction and reward your contribution to TVS Mobility's success.</p>

                <p>To enroll and activate your benefits, please click the link below:</p>

                <p><a href="{tracking_link}" style="color: blue; text-decoration: underline;">Activate Your Benefits Here</a></p>

                <p>Enrollment is open until [Insert Deadline]. Don't miss this opportunity to be part of this exciting new initiative!</p>

                <p>Thank you for your dedication and hard work.</p>

                <p>Best regards,<br>
                [CEO Name]<br>
                Chief Executive Officer<br>
                TVS Mobility</p>
            </body>
            </html>
            """

            # Create the MIME message
            msg = MIMEMultipart()
            msg['From'] = SENDER_EMAIL
            msg['To'] = recipient_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'html'))  # Send the email as HTML

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
