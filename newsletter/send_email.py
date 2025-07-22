import smtplib
from email.mime.text import MIMEText


def send_email(subject, body, sender, recipients, password):
    html_msg = MIMEText(body, "html")
    html_msg['Subject'] = subject
    html_msg['From'] = sender
    html_msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
        smtp_server.login(sender, password)
        smtp_server.sendmail(sender, recipients, html_msg.as_string())
    print("Message sent!")
