# -*- coding: utf-8 -*-

from odoo import models, fields, api


class analytic_account_cost_element(models.Model):
    _name = 'account.analytic.account.cost.element'

    @api.model
    def _compute_levels(self):
        result = []
        elements = self.env['project.cost_element'].search([])
        for element in elements:
            if (element.level, element.level) not in result:
                result.append((element.level, element.level))
        return result

    @api.onchange('level')
    def _onchange_level(self):
        if self.level:
            self.cost_element_id = False
            return {
                'domain': {
                    'cost_element_id': [('level', '=', self.level)]
                }
            }


    level           = fields.Selection('_compute_levels', string='Level')
    cost_element_id = fields.Many2one('project.cost_element', string='Cost Element')
    total_budget    = fields.Float('Total Budget')
    actual_budget   = fields.Float('Actual Budget', compute='compute_actual_budget', readonly=True)

    account_analytic_account_id = fields.Many2one('account.analytic.account')

    @api.multi
    def compute_actual_budget(self):
        for record in self:
            if record.account_analytic_account_id and record.account_analytic_account_id.id:
                lines = self.env['account.invoice.line'].search([
                    ('invoice_id.contract_id', '=', record.account_analytic_account_id.id),
                    ('cost_element_id', '=', record.cost_element_id.id),
                ])
                actual_budget = 0
                for line in lines:
                    actual_budget += line.price_subtotal
                record.actual_budget = actual_budget