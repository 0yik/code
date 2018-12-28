# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo import exceptions


class account_payment_term(models.Model):
    _inherit = 'account.payment.term'

    @api.one
    @api.constrains('overdue_percentage')
    def _check_valid_range(self):
        if self.overdue_percentage > 100 or self.overdue_percentage < 0:
            raise exceptions.Warning(_("Overdue Percentage only input from 0 to 100."))

    @api.onchange('overdue_percentage')
    def onchange_overdue_percentage(self):
        if self.overdue_percentage > 100 or self.overdue_percentage < 0:
            raise exceptions.Warning(_("Overdue Percentage only input from 0 to 100."))

    currency_id = fields.Many2one('res.currency', related='company_id.currency_id', readonly=True, store=True)
    overdue_charges_type = fields.Selection([('percentage', 'Percentage'), ('amount', 'Amount')], string='Overdue Charges Type', default='percentage')
    overdue_percentage = fields.Float(string='Overdue Percentage')
    overdue_type = fields.Selection([('daily', 'Daily'), ('monthly', 'Monthly')], string='Overdue Type')
    overdue_type_amount = fields.Selection([('daily', 'Daily'), ('monthly', 'Monthly')], string='Overdue Type')
    rate = fields.Monetary('Rate')
    computation_method = fields.Selection([('linear', 'Linear'), ('compounding', 'Compounding')], string='Computation Method', default='linear')

