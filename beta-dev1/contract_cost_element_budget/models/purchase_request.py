# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseRequest(models.Model):
    _inherit = 'purchase.request'

    contract_id = fields.Many2one('account.analytic.account', 'Contract')

    @api.model
    def create(self, values):
        record = super(PurchaseRequest, self).create(values)
        if record.contract_id and record.contract_id.id:
            for line in record.line_ids:
                if line.rfq_number and line.rfq_number.id:
                    line.rfq_number.contract_id = record.contract_id
        return record

    @api.multi
    def write(self, values):
        result = super(PurchaseRequest, self).write(values)
        for record in self:
            if record.contract_id and record.contract_id.id:
                for line in record.line_ids:
                    if line.rfq_number and line.rfq_number.id:
                        line.rfq_number.contract_id = record.contract_id
        return result