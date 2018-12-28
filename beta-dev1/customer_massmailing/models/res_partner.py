# -*- coding: utf-8 -*-
from odoo import models, api, fields, _

class ResPartner(models.Model):
    _inherit = "res.partner"

    def _mass_mail_count(self):
        for rec in self:
            rec.mass_mail_count = len(rec.find_mass_mails())

    def find_mass_mails(self):
        mass_mails = self.env['mail.mass_mailing'].search([('mailing_model','=', 'res.partner')])
        mass_mail_ids = []
        for mass in mass_mails:
            if set(self.ids).intersection(self.search(eval(mass.mailing_domain)).ids):
                mass_mail_ids.append(mass.id)
        return mass_mail_ids

    def get_mass_mail(self):
        mass_mail_ids = self.find_mass_mails()

        return {
            'name': _('Mass Mails'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'mail.mass_mailing',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', mass_mail_ids)],
            'context': self._context,
        }

    mass_mail_count = fields.Integer(compute="_mass_mail_count",string='Incomming Mail Server')