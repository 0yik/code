# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime

class Wizard(models.TransientModel):
    _name = 'account.analytic.budget.change'

    cost_element_id = fields.Many2one('project.cost_element', 'Cost Element')
    current_budget  = fields.Float('Current Budget', readonly=True)
    new_budget      = fields.Float('New Budget')
    remarks         = fields.Text('Remarks')

    @api.onchange('cost_element_id')
    def onchange_cost_element_id(self):
        context      = self.env.context
        active_model = context.get('active_model', False)
        active_id    = context.get('active_id', False)

        if active_id and active_model == 'account.analytic.account':
            contract = self.env['account.analytic.account'].browse(active_id)
            for record in self:
                if record.cost_element_id and record.cost_element_id.id:
                    line = contract.cost_element_ids.filtered(lambda r: r.cost_element_id.id == record.cost_element_id.id)
                    if line:
                        record.current_budget = line[0].total_budget

    @api.multi
    def action_confirm(self):
        context      = self.env.context
        active_model = context.get('active_model', False)
        active_id    = context.get('active_id', False)

        if active_id and active_model == 'account.analytic.account':
            contract = self.env['account.analytic.account'].browse(active_id)

            old_budget = 0
            for budget_log in contract.budget_log_ids :
                old_budget = budget_log.new_budget

            budget_log_data = {
                'old_budget': old_budget,
                'new_budget': self.new_budget,
                'cost_element_id': self.cost_element_id and self.cost_element_id.id,
                'remarks' : self.remarks,
                'date': fields.Date.today(),
                'user_id' : self.env.uid,
                'account_analytic_account_id': active_id,
            }

            budget_log_obj = self.env['account.analytic.account.budget.log']
            budget_log_obj.create(budget_log_data)

            corresponding_line = contract.cost_element_ids.filtered(lambda r: r.cost_element_id.id == self.cost_element_id.id)
            if corresponding_line:
                corresponding_line[0].total_budget = self.new_budget
            else:
                contract.cost_element_ids += contract.cost_element_ids.new({
                    'level': self.cost_element_id.level,
                    'cost_element_id': self.cost_element_id.id,
                    'total_budget' : self.new_budget,
                })

        return True