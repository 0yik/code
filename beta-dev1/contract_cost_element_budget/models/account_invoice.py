# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountInvoiceContract(models.Model):
    _inherit = 'account.invoice'

    contract_id = fields.Many2one('account.analytic.account', 'Contract')

    @api.model
    def default_get(self, fields):
        result = super(AccountInvoiceContract, self).default_get(fields)
        purchase_ids = self.env.context.get('active_ids', [])
        active_model = self.env.context.get('active_model', False)
        if active_model == 'purchase.order' and purchase_ids:
            for purchase in self.env['purchase.order'].browse(purchase_ids):
                if purchase.contract_id and purchase.contract_id.id:
                    result['contract_id'] = purchase.contract_id.id
        return result