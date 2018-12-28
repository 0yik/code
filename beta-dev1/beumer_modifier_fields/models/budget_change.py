# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Wizard(models.TransientModel):
    _inherit = 'account.analytic.budget.change'

    project_id = fields.Many2one('account.analytic.account', 'Project')
    volog_change_id = fields.Many2one('vo.log.change', 'VO Change Reference')

    @api.model
    def default_get(self, fields):
        res = super(Wizard, self).default_get(fields)
        if self.env.context.get('active_model', False) == 'account.analytic.account':
            active_id =  self.env.context.get('active_id', False)
            if res is None:
                res = {}
            res['project_id'] = active_id
        return res

    @api.onchange('cost_element_id')
    def onchange_cost_element_id(self):
        context      = self.env.context
        active_model = context.get('active_model', False)
        active_id    = context.get('active_id', False)

        if active_id and active_model == 'account.analytic.account':
            contract = self.env['account.analytic.account'].browse(active_id)
            for record in self:
                if record.cost_element_id and record.cost_element_id.id:
                    line = contract.cost_element_ids.filtered(lambda r: r.cost_element_id3 and (r.cost_element_id3.id == record.cost_element_id.id))
                    if line:
                        record.current_budget = line[0].total_budget

    @api.onchange('project_id')
    def onchange_project_id(self):
        cost_element_ids = []
        if self.env.context.get('active_model', False) == 'account.analytic.account':
            active_id =  self.env.context.get('active_id', False)
            if active_id:
                project = self.env['account.analytic.account'].browse(active_id)
                for cost_element in project.cost_element_ids:
                    if cost_element.cost_element_id3 and cost_element.cost_element_id3.id:
                        if cost_element.cost_element_id3.id not in cost_element_ids:
                            cost_element_ids.append(cost_element.cost_element_id3.id)

        result = {
            'domain': {
                'cost_element_id': [('id', 'in', cost_element_ids)],
                'volog_change_id': [('project_id', '=', active_id)],
            }
        }
        return result

    @api.multi
    def action_confirm(self):
        context = self.env.context
        active_model = context.get('active_model', False)
        active_id = context.get('active_id', False)

        if active_id and active_model == 'account.analytic.account':
            contract = self.env['account.analytic.account'].browse(active_id)

            for record in self:
                old_budget = 0
                if record.cost_element_id and record.cost_element_id.id:
                    line = contract.cost_element_ids.filtered(lambda r: r.cost_element_id3 and (r.cost_element_id3.id == record.cost_element_id.id))
                    if line:
                        old_budget = line[0].total_budget

                budget_log_obj = self.env['account.analytic.account.budget.log']
                budget_log_ids = budget_log_obj.search([('account_analytic_account_id', '=', active_id)])
                count = len(budget_log_ids) + 1
                budge_change_number = "BC%s" % ('{0:02}'.format(count))

                if budge_change_number:
                    budget_log_data = {
                        'budge_change_number': budge_change_number,
                        'volog_change_id' : self.volog_change_id and self.volog_change_id.id,
                        'old_budget': old_budget,
                        'new_budget': self.new_budget,
                        'cost_element_id': self.cost_element_id and self.cost_element_id.id,
                        'remarks': self.remarks,
                        'date': fields.Date.today(),
                        'user_id': self.env.uid,
                        'account_analytic_account_id': active_id,
                    }
                budget_log_obj.create(budget_log_data)

                corresponding_line = contract.cost_element_ids.filtered(lambda r: r.cost_element_id3 and (r.cost_element_id3.id == self.cost_element_id.id))
                if corresponding_line:
                    corresponding_line[0].total_budget = record.new_budget

        return True