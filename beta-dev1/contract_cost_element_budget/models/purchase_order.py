# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseOrderContract(models.Model):
    _inherit = 'purchase.order'

    contract_id = fields.Many2one('account.analytic.account', 'Contract')