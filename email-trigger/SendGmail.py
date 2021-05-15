
import smtplib, ssl
from email.mime.text import MIMEText as text

class SendEmail(object):

    def __init__(self):
        self.email_id = "_xxxx_@gmail.com"
        self.email_password = "pwd"

    def send_email(self, subject, msg):
        FROM = self.email_id
        TO = ['<email_id>']
        CC = ['<email_id>', '<email_id>']
        SUBJECT = subject
        TEXT = msg

        # Prepare actual message
        m = text(msg)
        m['Subject'] = 'Sample Email'
        m['From'] = FROM
        m['To'] = ','.join(TO)


        try:
            print("Sending Email... ")
            context = ssl.create_default_context()
            server = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context)
            # server.ehlo()
            # server.starttls()
            server.login(self.email_id, self.email_password)
            server.sendmail(FROM, TO, m.as_string())
            server.close()
            print('Email Sent Successfully')
        except Exception as e:
            print(e)
            print("Failed to send email")

