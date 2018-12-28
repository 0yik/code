# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    report_display_number = fields.Char('Name Display', compute='_get_drums_info')

    @api.multi
    def _get_drums_info(self):
        for record in self:
            return record.update({
                'report_display_number': record.number.split('/')[-1],
            })
