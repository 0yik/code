# -*- coding: utf-8 -*-

from odoo import models, fields, api

class aikchin_modifier_partner_ledger(models.TransientModel):
    _inherit = 'account.report.partner.ledger'

    partner_ids = fields.One2many('partner.ledger.line.partners','partner_ledger_id',string='Partners')

class partner_ledger_line_partners(models.TransientModel):
    _name = 'partner.ledger.line.partners'

    def _check_result_selection(self):
        if 'result_selection' in self._context:
            return self._context.get('result_selection')
        return True

    name = fields.Many2one('res.partner',string="Name")
    payment_term = fields.Many2many('account.payment.term')
    partner_ledger_id = fields.Many2one('account.report.partner.ledger')
    result_selection = fields.Char(default=_check_result_selection)
    partner_ledger_balance_id = fields.Many2one('account.aged.trial.balance')

    @api.onchange('result_selection')
    def onchange_result_selection(self):
        if self.result_selection == 'customer':
            return {'domain': {'name': [('customer', '=', True)]}}
        elif self.result_selection == 'supplier':
            return {'domain': {'name': [('supplier', '=', True)]}}
        else:
            return {'domain': {'name': ['|', ('customer', '=', True), ('supplier', '=', True)]}}

    @api.onchange('name')
    def onchange_name(self):
        if self.name:
            if self.result_selection == 'customer':
                self.payment_term = self.name.property_payment_term_ids
                return {'domain': {'payment_term': [('id', 'in', self.payment_term.ids)]}}
            elif self.result_selection == 'supplier':
                self.payment_term = self.name.property_supplier_payment_term_ids
                return {'domain': {'payment_term': [('id', 'in', self.payment_term.ids)]}}
            else:
                self.payment_term = self.name.property_payment_term_ids + self.name.property_supplier_payment_term_ids
                return {'domain': {'payment_term': [('id', 'in', self.payment_term.ids)]}}



