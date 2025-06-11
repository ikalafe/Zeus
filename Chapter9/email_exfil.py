import smtplib
import time
import win32com.client

smtp_server = 'smtp.example.com'
smtp_port = 587
smtp_acct = 'imkalafe@gmail.com'
smtp_password = 'secret'
tgt_accts = ['daniyaldehghan2021@gmail.com']

def plain_email(subject, contents):
    message = f'Subject: {subject}\nFrom {smtp_acct}\n'
    message += f'To: {tgt_accts}\n\n{contents.decode()}'
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_acct, tgt_accts, message)
    server.quit()