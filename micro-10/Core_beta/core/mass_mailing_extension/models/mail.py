from email import Encoders
from email.charset import Charset
from email.header import Header
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formataddr, formatdate, getaddresses, make_msgid
import logging
import re
import smtplib
import threading

from odoo import api, fields, models, tools, _
from odoo.exceptions import except_orm, UserError
from odoo.tools import html2text, ustr

_logger = logging.getLogger(__name__)
_test_logger = logging.getLogger('odoo.tests')


class MailDeliveryException(except_orm):
    """Specific exception subclass for mail delivery errors"""
    def __init__(self, name, value):
        super(MailDeliveryException, self).__init__(name, value)


class WriteToLogger(object):
    """debugging helper: behave as a fd and pipe to logger at the given level"""
    def __init__(self, logger, level=logging.DEBUG):
        self.logger = logger
        self.level = level

    def write(self, s):
        self.logger.log(self.level, s)


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


def encode_header(header_text):
    """Returns an appropriate representation of the given header value,
       suitable for direct assignment as a header value in an
       email.message.Message. RFC2822 assumes that headers contain
       only 7-bit characters, so we ensure it is the case, using
       RFC2047 encoding when needed.

       :param header_text: unicode or utf-8 encoded string with header value
       :rtype: string | email.header.Header
       :return: if ``header_text`` represents a plain ASCII string,
                return the same 7-bit string, otherwise returns an email.header.Header
                that will perform the appropriate RFC2047 encoding of
                non-ASCII values.
    """
    if not header_text:
        return ""
    # convert anything to utf-8, suitable for testing ASCIIness, as 7-bit chars are
    # encoded as ASCII in utf-8
    header_text_utf8 = ustr(header_text).encode('utf-8')
    header_text_ascii = try_coerce_ascii(header_text_utf8)
    # if this header contains non-ASCII characters,
    # we'll need to wrap it up in a message.header.Header
    # that will take care of RFC2047-encoding it as
    # 7-bit string.
    return header_text_ascii or Header(header_text_utf8, 'utf-8')


def encode_header_param(param_text):
    """Returns an appropriate RFC2047 encoded representation of the given
       header parameter value, suitable for direct assignation as the
       param value (e.g. via Message.set_param() or Message.add_header())
       RFC2822 assumes that headers contain only 7-bit characters,
       so we ensure it is the case, using RFC2047 encoding when needed.

       :param param_text: unicode or utf-8 encoded string with header value
       :rtype: string
       :return: if ``param_text`` represents a plain ASCII string,
                return the same 7-bit string, otherwise returns an
                ASCII string containing the RFC2047 encoded text.
    """
    # For details see the encode_header() method that uses the same logic
    if not param_text:
        return ""
    param_text_utf8 = ustr(param_text).encode('utf-8')
    param_text_ascii = try_coerce_ascii(param_text_utf8)
    return param_text_ascii or Charset('utf8').header_encode(param_text_utf8)


address_pattern = re.compile(r'([^ ,<@]+@[^> ,]+)')

def extract_rfc2822_addresses(text):
    """Returns a list of valid RFC2822 addresses
       that can be found in ``source``, ignoring
       malformed ones and non-ASCII ones.
    """
    if not text:
        return []
    candidates = address_pattern.findall(ustr(text).encode('utf-8'))
    return filter(try_coerce_ascii, candidates)


def encode_rfc2822_address_header(header_text):
    """If ``header_text`` contains non-ASCII characters,
       attempts to locate patterns of the form
       ``"Name" <address@domain>`` and replace the
       ``"Name"`` portion by the RFC2047-encoded
       version, preserving the address part untouched.
    """
    def encode_addr(addr):
        name, email = addr
        if not try_coerce_ascii(name):
            name = str(Header(name, 'utf-8'))
        return formataddr((name, email))

    addresses = getaddresses([ustr(header_text).encode('utf-8')])
    return COMMASPACE.join(map(encode_addr, addresses))




class IrMailServer(models.Model):
    """Represents an SMTP server, able to send outgoing emails, with SSL and TLS capabilities."""
    _inherit = "ir.mail_server"

    def build_email(self, email_from, email_to, subject, body, email_cc=None, email_bcc=None, reply_to=False,
                    attachments=None, message_id=None, references=None, object_id=False, subtype='plain', headers=None,
                    body_alternative=None, subtype_alternative='plain'):
        """Constructs an RFC2822 email.message.Message object based on the keyword arguments passed, and returns it.

           :param string email_from: sender email address
           :param list email_to: list of recipient addresses (to be joined with commas) 
           :param string subject: email subject (no pre-encoding/quoting necessary)
           :param string body: email body, of the type ``subtype`` (by default, plaintext).
                               If html subtype is used, the message will be automatically converted
                               to plaintext and wrapped in multipart/alternative, unless an explicit
                               ``body_alternative`` version is passed.
           :param string body_alternative: optional alternative body, of the type specified in ``subtype_alternative``
           :param string reply_to: optional value of Reply-To header
           :param string object_id: optional tracking identifier, to be included in the message-id for
                                    recognizing replies. Suggested format for object-id is "res_id-model",
                                    e.g. "12345-crm.lead".
           :param string subtype: optional mime subtype for the text body (usually 'plain' or 'html'),
                                  must match the format of the ``body`` parameter. Default is 'plain',
                                  making the content part of the mail "text/plain".
           :param string subtype_alternative: optional mime subtype of ``body_alternative`` (usually 'plain'
                                              or 'html'). Default is 'plain'.
           :param list attachments: list of (filename, filecontents) pairs, where filecontents is a string
                                    containing the bytes of the attachment
           :param list email_cc: optional list of string values for CC header (to be joined with commas)
           :param list email_bcc: optional list of string values for BCC header (to be joined with commas)
           :param dict headers: optional map of headers to set on the outgoing mail (may override the
                                other headers, including Subject, Reply-To, Message-Id, etc.)
           :rtype: email.message.Message (usually MIMEMultipart)
           :return: the new RFC2822 email message
        """
        email_from = email_from or tools.config.get('email_from')
        assert email_from, "You must either provide a sender address explicitly or configure "\
                           "a global sender address in the server configuration or with the "\
                           "--email-from startup parameter."

        # Note: we must force all strings to to 8-bit utf-8 when crafting message,
        #       or use encode_header() for headers, which does it automatically.

        headers = headers or {}         # need valid dict later
        email_cc = email_cc or []
        email_bcc = email_bcc or []
        body = body or u''

        email_body_utf8 = ustr(body).encode('utf-8')
        email_text_part = MIMEText(email_body_utf8, _subtype=subtype, _charset='utf-8')
        msg = MIMEMultipart()

        if not message_id:
            if object_id:
                message_id = tools.generate_tracking_message_id(object_id)
            else:
                message_id = make_msgid()
        msg['Message-Id'] = encode_header(message_id)
        if references:
            msg['references'] = encode_header(references)
        msg['Subject'] = encode_header(subject)
        msg['From'] = encode_rfc2822_address_header(email_from)
        # del msg['Reply-To']
        # if reply_to:
        #     msg['Reply-To'] = encode_rfc2822_address_header(reply_to)
        # else:
        #     msg['Reply-To'] = msg['From']
        msg['Reply-To'] = ''
        msg['To'] = encode_rfc2822_address_header(COMMASPACE.join(email_to))
        if email_cc:
            msg['Cc'] = encode_rfc2822_address_header(COMMASPACE.join(email_cc))
        if email_bcc:
            msg['Bcc'] = encode_rfc2822_address_header(COMMASPACE.join(email_bcc))
        msg['Date'] = formatdate()
        # Custom headers may override normal headers or provide additional ones
        for key, value in headers.iteritems():
            msg[ustr(key).encode('utf-8')] = encode_header(value)

        if subtype == 'html' and not body_alternative and html2text:
            # Always provide alternative text body ourselves if possible.
            text_utf8 = tools.html2text(email_body_utf8.decode('utf-8')).encode('utf-8')
            alternative_part = MIMEMultipart(_subtype="alternative")
            alternative_part.attach(MIMEText(text_utf8, _charset='utf-8', _subtype='plain'))
            alternative_part.attach(email_text_part)
            msg.attach(alternative_part)
        elif body_alternative:
            # Include both alternatives, as specified, within a multipart/alternative part
            alternative_part = MIMEMultipart(_subtype="alternative")
            body_alternative_utf8 = ustr(body_alternative).encode('utf-8')
            alternative_body_part = MIMEText(body_alternative_utf8, _subtype=subtype_alternative, _charset='utf-8')
            alternative_part.attach(alternative_body_part)
            alternative_part.attach(email_text_part)
            msg.attach(alternative_part)
        else:
            msg.attach(email_text_part)

        if attachments:
            for (fname, fcontent) in attachments:
                filename_rfc2047 = encode_header_param(fname)
                part = MIMEBase('application', "octet-stream")

                # The default RFC2231 encoding of Message.add_header() works in Thunderbird but not GMail
                # so we fix it by using RFC2047 encoding for the filename instead.
                part.set_param('name', filename_rfc2047)
                part.add_header('Content-Disposition', 'attachment', filename=filename_rfc2047)

                part.set_payload(fcontent)
                Encoders.encode_base64(part)
                msg.attach(part)
        return msg
