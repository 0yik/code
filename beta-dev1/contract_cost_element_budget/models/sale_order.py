# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrderContract(models.Model):
    _inherit = 'sale.order'

    contract_id   = fields.Many2one('account.analytic.account', 'Contract')

    @api.multi
    def _prepare_invoice(self):
        self.ensure_one()
        result = super(SaleOrderContract, self)._prepare_invoice()
        if type(result) is dict:
            result['contract_id'] = self.contract_id and self.contract_id.id
        return result