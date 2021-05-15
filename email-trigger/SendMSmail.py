
import smtplib, ssl
from email.mime.text import MIMEText as text

class SendEmail(object):

    def __init__(self):
        self.email_id = "<outlook_email_id>"
        self.email_password = "<pwd>"

    def send_email(self, subject, msg):
        FROM = self.email_id
        TO = ['<email_id>']
        CC = ['<email_id>', '<email_id>']
        SUBJECT = subject
        TEXT = msg

        # Prepare actual message
        message = text(msg)
        message['Subject'] = 'Hello!'
        message['From'] = FROM
        message['To'] = ','.join(TO)
        import pdb; pdb.set_trace();
        try:
            print("Sending Email... ")
            context = ssl.create_default_context()
            server = smtplib.SMTP('smtp.office365.com', 587)
            # server.ehlo()
            # server.starttls()
            server.login(self.email_id, self.email_password)
            server.sendmail(FROM, TO, message.as_string())
            server.close()
            print('Email Sent Successfully')
        except Exception as e:
            print(e)
            print("Failed to send email")

