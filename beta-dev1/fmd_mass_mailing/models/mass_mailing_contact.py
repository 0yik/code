# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime,date

class MailMassMailingContact(models.Model):
    _inherit='mail.mass_mailing.contact'

    name = fields.Many2one("res.partner", string="Name", required=True, domain=[('customer', '=', True)])
    email = fields.Char(required=True)
    
    @api.onchange('name')
    def _onchange_name(self):
        email = ''
        if self.name and self.name.email_f and not self.name.opt_out_f:
            email += self.name.email_f+','
        else:
            email = email
        if self.name and self.name.email_s and not self.name.opt_out_s:
            email += self.name.email_s+','
        else:
            email = email
        if self.name and self.name.email_t and not self.name.opt_out_t:
            email += self.name.email_t+','
        else:
            email = email
        if self.name:
            for line in self.name.contact_list_line:
                if line.email and not line.opt_out_c:
                    email += line.email+','
                else:
                    email = email
        self.email = email