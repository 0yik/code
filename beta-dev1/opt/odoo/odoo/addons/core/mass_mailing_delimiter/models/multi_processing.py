import multiprocessing
from  multiprocessing import Pool
from datetime import datetime
import smtplib
from odoo import tools
from odoo.tools import html2text, ustr
from odoo.exceptions import except_orm, UserError
import re
import time
import logging

_logger = logging.getLogger(__name__)


def _multiprocessing_mass_mailing_min(msg, smtp_attrs):
    # parse res_id for 1 min
    Mail_Limit_Min = 150
    parse_msg = [msg[i:i + Mail_Limit_Min] for i in range(0, len(msg), Mail_Limit_Min)]
    for res in parse_msg:
        now = datetime.now()
        _multiprocessing_mass_mailing(res, smtp_attrs)
        now = (datetime.now() - now).seconds
        if now >= 60:
            continue
        else:
            time.sleep(60 - now)
    return


def _multiprocessing_mass_mailing(msg, smtp_attrs):

    process_num = int(len(msg) / 20)
    if len(msg)%20 != 0:
        process_num += 1
    parse_res_id = [msg[i:i + 20] for i in range(0, len(msg), 20)]
    for record in parse_res_id:
        record.append(smtp_attrs)
    poll = Pool(process_num)
    res = poll.map(_send_email, parse_res_id)
    poll.close()


def _send_email(data):
    smtp_attrs = data[-1]
    data = data[:-1]
    smtp = False

    smtp_server = smtp_attrs.get('smtp_server')
    smtp_port = smtp_attrs.get('smtp_port')
    smtp_user = smtp_attrs.get('smtp_user')
    smtp_password = smtp_attrs.get('smtp_password')
    smtp_encryption = smtp_attrs.get('smtp_encryption')

    smtp_server = smtp_server or tools.config.get('smtp_server')
    smtp_port = tools.config.get('smtp_port', 25) if smtp_port is None else smtp_port
    smtp_user = smtp_user or tools.config.get('smtp_user')
    smtp_password = smtp_password or tools.config.get('smtp_password')
    if smtp_encryption is None and tools.config.get('smtp_ssl'):
        smtp_encryption = 'starttls'  # STARTTLS is the new meaning of the smtp_ssl flag as of v7.0
    try:
        try:
            smtp = connect(smtp_server, smtp_port, smtp_user, smtp_password, smtp_encryption or False)
        except:
            return
        if smtp:
            for record in data:
                send_email(record, smtp)
    finally:
        if smtp:
            smtp.quit()


def connect(host=None, port=None, user=None, password=None, encryption=False, smtp_debug=False):

    if encryption == 'ssl':
        connection = smtplib.SMTP_SSL(host, port)
    else:
        connection = smtplib.SMTP(host, port)
    if encryption == 'starttls':
        connection.starttls()

    if user:
        user = ustr(user).encode('utf-8')
        password = ustr(password).encode('utf-8')
        connection.login(user, password)
    return connection


address_pattern = re.compile(r'([^ ,<@]+@[^> ,]+)')


def try_coerce_ascii(string_utf8):
    """Attempts to decode the given utf8-encoded string
       as ASCII after coercing it to UTF-8, then return
       the confirmed 7-bit ASCII string.

       If the process fails (because the string
       contains non-ASCII characters) returns ``None``.
    """
    try:
        string_utf8.decode('ascii')
    except UnicodeDecodeError:
        return
    return string_utf8


def extract_rfc2822_addresses(text):
    """Returns a list of valid RFC2822 addresses
       that can be found in ``source``, ignoring
       malformed ones and non-ASCII ones.
    """
    if not text:
        return []
    candidates = address_pattern.findall(ustr(text).encode('utf-8'))
    return filter(try_coerce_ascii, candidates)


def send_email(message, smtp):
    smtp_from = message['Return-Path'] or message['From']

    # The email's "Envelope From" (Return-Path), and all recipient addresses must only contain ASCII characters.
    from_rfc2822 = extract_rfc2822_addresses(smtp_from)
    assert from_rfc2822, ("Malformed 'Return-Path' or 'From' address: %r - "
                          "It should contain one valid plain ASCII email") % smtp_from
    # use last extracted email, to support rarities like 'Support@MyComp <support@mycompany.com>'
    smtp_from = from_rfc2822[-1]
    email_to = message['To']
    email_cc = message['Cc']
    email_bcc = message['Bcc']

    smtp_to_list = filter(None, tools.flatten(map(extract_rfc2822_addresses, [email_to, email_cc, email_bcc])))

    x_forge_to = message['X-Forge-To']
    if x_forge_to:
        # `To:` header forged, e.g. for posting on mail.channels, to avoid confusion
        del message['X-Forge-To']
        del message['To']  # avoid multiple To: headers!
        message['To'] = x_forge_to

    try:
        message_id = message['Message-Id']
        # Add email in Maildir if smtp_server contains maildir.
        try:
            smtp.sendmail(smtp_from, smtp_to_list, message.as_string())
        finally:
            pass
    except Exception as e:
        msg = "Mail delivery failed via SMTP server"
        _logger.info(msg)
        return message_id
