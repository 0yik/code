# -*- coding: utf-8 -*-
from odoo import fields, models

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

    purchase_id = fields.Many2one('purchase.order', 'Purchase Order')
    work_order_id = fields.Many2one('work.order', 'Work Order')

AccountInvoice()