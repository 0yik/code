# -*- coding: utf-8 -*-

import smtplib
import xmlrpclib
import gearman
import json

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

DB   = 'hashmicro'
USER = 'ricky.halim@hashmicro.com'
PASS = 'Hash7900Micro'
ROOT = 'http://localhost:8069/xmlrpc/'

def get_uid():
    uid = xmlrpclib.ServerProxy(ROOT + 'common').login(DB, USER, PASS)
    print "Logged in as %s (uid: %d)" % (USER, uid)
    return uid

def get_servers():
    uid     = get_uid()
    sock    = xmlrpclib.ServerProxy(ROOT + 'object')
    servers = sock.execute(DB, uid, PASS, 'mailing.queue', 'get_servers', {})
    print "Servers: %s" % (servers)
    return servers

def get_worker():
    servers = get_servers()
    worker  = gearman.GearmanWorker(servers)
    return worker

def email_callback(gearman_worker, job):
    print "Email Callback %s" % (job.data,)
    decoded = json.loads(job.data)
    # data = json.loads(job.data)
    # if 'msg' in data:
    #    data['msg'] = pickle.loads(data['msg'])

    email_from = decoded['general'].get('email_from')
    email_tos  = decoded['data'].get('email_to')

    s = smtplib.SMTP(decoded['smtp'].get('smtp_server'), decoded['smtp'].get('smtp_port'))
    s.login(decoded['smtp'].get('smtp_user'), decoded['smtp'].get('smtp_password'))
    for email_to in email_tos:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = decoded['general'].get('subject')
        msg['From'] = email_from
        msg['To'] = email_to

        html = decoded['data'].get('body')
        part = MIMEText(html, 'html')

        msg.attach(part)

        s.sendmail(email_from, email_to, msg.as_string())
    s.quit()

    return 'ok'

worker = get_worker()
worker.register_task('send_mail', email_callback)
worker.work()