# -*- coding: utf-8 -*-

from odoo import models, fields


class ServiceCharge(models.Model):
    _name = 'service.charge'

    name = fields.Char(string='Service Charge Name', required=True)
    service_charge_computation = fields.Selection([('fixed', 'Fixed'), ('percentage_of_price', 'Percentage Of Price')], required=True)
    amount = fields.Float(string='Amount',)
    service_charge_account_id = fields.Many2one('account.account', 'Service Charge Account')
    service_charge_account_refund_id = fields.Many2one('account.account', 'Service Charge Account On Refunds')

    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
