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


class vieterp_ir_mail_server(models.Model):
    _inherit = 'ir.mail_server'
    _name = 'ir.mail_server.outgoing'

    @api.model
    def send_email(self, message, mail_server_id=None, smtp_server=None, smtp_port=None,
                   smtp_user=None, smtp_password=None, smtp_encryption=None, smtp_debug=False):
        if not mail_server_id:
            raise UserError(_("Missing SMTP Server") + "\n" + _(
                "Please define at least one SMTP server, or provide the SMTP parameters explicitly."))
        res = super(vieterp_ir_mail_server, self).send_email(message, mail_server_id, smtp_server, smtp_port, smtp_user,
                                                             smtp_password, smtp_encryption, smtp_debug)
        return res

class ir_mail_server(models.Model):
    _inherit = 'ir.mail_server'

    email_line_ids = fields.One2many('ir.mail_server.email.line', 'server_id', string='Line Ids')

    @api.model
    def create(self, vals):
        res = super(ir_mail_server, self).create(vals)
        if res.smtp_user:
            res.email_line_ids.create({'name': res.smtp_user, 'server_id': res.id})
        return res

class ir_mail_server_email_line(models.Model):
    _name = 'ir.mail_server.email.line'

    name = fields.Char('Name')
    server_id = fields.Many2one('ir.mail_server', 'Server ID')

