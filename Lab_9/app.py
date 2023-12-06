from flask import Flask, jsonify, render_template, request, redirect, url_for
from smtplib import SMTP, SMTPException
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from ftplib import FTP, all_errors
from os import getenv, mkdir
from shutil import rmtree
from dotenv import load_dotenv

mkdir('uploads')
load_dotenv()
from_address = getenv('FROM_ADDRESS')

app = Flask(__name__)


@app.route('/', methods=['GET'])
def email_form():
    return render_template('index.html')


@app.route('/send', methods=['POST'])
def send_email():
    to_address = request.form.get('recipient_email')
    subject = request.form.get('email_subject')
    body = request.form.get('email_body')

    file_link = ''
    if request.files['file'].filename != '':
        file = request.files['file']
        file.save(f'uploads/{file.filename}')

        if upload_file(file.filename):
            file_link = f"ftp://{getenv('FTP_USERNAME')}:{getenv('FTP_PASSWORD')}@{getenv('FTP_SERVER')}/home/somedirectory/{getenv('FTP_WD')}/{file.filename}"          

    if send_email(to_address, subject, body, file_link):
        return jsonify('Email was sent successfully!', 200)
    else:
        return jsonify('An error occured in sending email!', 500)
    

def upload_file(filename: str) -> bool:
    try:
        ftp = FTP(getenv('FTP_SERVER'))
        ftp.login(user=getenv('FTP_USERNAME'), passwd=getenv('FTP_PASSWORD'))
        ftp.cwd(getenv('FTP_WD'))

        file_list = ftp.nlst()
        if filename not in file_list:
            with open(f'uploads/{filename}', 'rb') as file:
                ftp.storbinary(f'STOR {filename}', file)

        ftp.quit()
        return True

    except all_errors:
        print('Error in storing file on ftp server')
        return False


def send_email(to_address: str, subject: str, body: str, ftp_link: str) -> bool:
    try:
        with SMTP(getenv('SMTP_SERVER'), 587) as server:
            server.starttls()
            server.login(from_address, getenv('APP_PASSWORD'))

            message = MIMEMultipart()
            message['Subject'] = subject
            message['From'] = from_address
            message['To'] = to_address

            if ftp_link != '':
                body += f'\n\nFile attached: {ftp_link}'

            message.attach(MIMEText(body, 'plain'))
            server.sendmail(from_address, to_address, message.as_string())

            server.quit()  
            return True
         
    except SMTPException as sme:
        print(f'Email server error: {sme}')
        return False


if __name__ == '__main__':
    app.run(debug=False)
    rmtree('uploads')