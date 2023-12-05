from flask import Flask, render_template
from smtplib import SMTP
from email.mime.text import MIMEText
from os import getenv
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)


@app.route('/', methods=['GET'])
def email_form():
    send_email()
    return render_template('index.html')


def send_email():
    with SMTP('smtp.gmail.com', 587) as server:
        server.starttls()

        from_address = 'sevabaj@gmail.com'
        to_address = 'sevabaj@gmail.com'

        server.login(from_address, getenv('APP_PASSWORD'))

        message = MIMEText("This is the message body.")
        message["Subject"] = "Test Subject"
        message["From"] = from_address
        message["To"] = to_address

        server.sendmail(from_address, to_address, f"MAIL FROM: <{from_address}>")
        server.sendmail(from_address, to_address, f"RCPT TO: <{to_address}>")
        server.sendmail(from_address, to_address, message.as_string())

        server.quit()        


if __name__ == '__main__':
    app.run(debug=False)