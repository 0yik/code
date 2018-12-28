# -*- coding: utf-8 -*-

from odoo import models, fields, api

class my_account(models.Model):
    _inherit = 'account.invoice'

    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_compute_amount', default=0)

    @api.model
    def update_null_amount_total(self):
        self.env.cr.execute("""
            UPDATE account_invoice SET amount_total = 0 WHERE amount_total IS NULL;
        """)