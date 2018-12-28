# -*- coding: utf-8 -*-

from odoo import models, fields


class OrderCharge(models.Model):
    _name = 'order.charge'

    name = fields.Char(string='Name', required=True)
    type = fields.Selection([('fixed', 'Fixed'), ('percentage', 'Percentage')], required=True)
    amount = fields.Float(string='Amount',)
    order_charge_account_id = fields.Many2one('account.account', 'Delivery Charge Account')
    order_charge_account_refund_id = fields.Many2one('account.account', 'Delivery Charge Account On Refunds')