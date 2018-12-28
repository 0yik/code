# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import models, fields, api,_
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT


class Asset(models.Model):
    _inherit = 'account.asset.asset'

    is_apply_notification = fields.Boolean('Apply Notification')
    emails = fields.Many2many('res.users', string="Emails")
    date_before_notification = fields.Integer("Date Before Notification", default=10)

    @api.multi
    def set_as_open(self):
        for rec in self.search([]):
            if rec.is_apply_notification:
                if rec.emails:
                    depreciation_date = datetime.now().date() + relativedelta(days=rec.date_before_notification)
                    domain = [
                        "|",
                        ('depreciation_date', '=', datetime.now().date().strftime(DEFAULT_SERVER_DATE_FORMAT)),
                        ('depreciation_date', '=', depreciation_date),
                        ('asset_id', '=', rec.id),
                    ]
                    base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
                    url = base_url + '/web#id=%s&view_type=form&model=account.asset.asset' % (rec.id)
                    for line in self.env['account.asset.depreciation.line'].search(domain):

                        email_from = self.company_id.email or 'Administrator <admin@example.com>'
                        for partner in rec.emails.mapped('partner_id'):
                            subject = 'Asset Notification'
                            message = """
                                        <html>
                                            <head>
                                                Dear %s,
                                            </head>
                                            <body>
                                               You have an Asset <a href="%s" target="_blank">%s</a> need to generate. <br/>
                                               Requestor: %s.
                                            </body>
                                        <html>""" % ( partner.name, url, line.asset_id.name, rec.responsible_id.user_id.partner_id.name)

                            mail_message = {
                                'subject': subject,
                                'email_from': email_from,
                                'body': message,
                                'partner_ids': [(6, 0, [partner.id])],
                                'needaction_partner_ids': [(6, 0, [partner.id])]
                            }
                            thread_pool = self.env['mail.message'].create(mail_message)
                            thread_pool.needaction_partner_ids = [(6, 0, [partner.id])]

                            email_out = {
                                'state': 'outgoing',
                                'subject': subject,
                                'body_html': '<pre>%s</pre>' % message,
                                'email_to': partner.email,
                                'email_from': email_from,
                            }
                            self.env['mail.mail'].create(email_out)
