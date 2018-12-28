# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    
    user_debit = fields.Float(string="Debit", copy=False)
    user_credit = fields.Float(string="Credit", copy=False)

    @api.model
    def create(self, vals):
        res = super(AccountMoveLine, self).create(vals)
        if not vals.get('currency_id') and (res.user_debit or res.user_credit):
            res.currency_id = res.company_id.currency_id.id
        if res.company_id.currency_id.id != res.currency_id.id :
            if res.user_debit and res.currency_id.rate:
                res.debit = res.user_debit * res.currency_id.rate
            if res.user_credit and res.currency_id.rate:
                res.credit = res.user_credit * res.currency_id.rate
        if res.company_id.currency_id.id == res.currency_id.id :
            res.debit = res.user_debit
            res.credit = res.user_credit
        return res

    @api.multi
    def write(self, vals):
        res = super(AccountMoveLine, self).write(vals)
        if self.company_id.currency_id.id != self.currency_id.id and (vals.get('user_debit') or vals.get('currency_id')) and self.currency_id.rate:
            self.debit = self.user_debit * self.currency_id.rate
        if self.company_id.currency_id.id != self.currency_id.id and (vals.get('user_credit')or vals.get('currency_id')) and self.currency_id.rate:
            self.credit = self.user_credit * self.currency_id.rate
        if self.company_id.currency_id.id == self.currency_id.id and vals.get('currency_id') or vals.get('user_debit') or vals.get('user_credit'):
            self.debit = self.user_debit
            self.credit = self.user_credit
        return res
