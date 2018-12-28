# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class account_payment(models.Model):
    _inherit = "account.payment"

    @api.model
    def default_get(self, fields):
        rec = super(account_payment, self).default_get(fields)
        if rec.get('amount', False):
        	amount = rec.get('amount', False)
        	if amount > 0:
        		amt = amount / 2
        		rec['amount'] = amt
        return rec
