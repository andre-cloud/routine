#!/data/bin/python_env/bin/python

import os, sys
import smtplib

from src.defaults import SMTP_SERVER_IP, DEFAULT_MAIL

SMTP = SMTP_SERVER_IP
sender = DEFAULT_MAIL


def send_mail(mail, jobid):
    try:
        with open('README.md') as f:
            text = f.read()

        text = f'''From: SLURM <{sender}>
Subject: Calculation of {jobid}

{text}
        '''

        smtpObj = smtplib.SMTP(SMTP)
        smtpObj.sendmail(sender, mail, text)
        print('Mail correctly sent')

    except smtplib.SMTPException:
        print('Mail correctly sent')

if __name__=='__main__':
    mail, jobid = sys.argv[1:]
    send_mail(mail, jobid)

