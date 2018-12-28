# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountAnalyticLine(models.Model):
    _inherit = "account.analytic.line"

    budget_planned_amount = fields.Float('Budget',store=True)

#     @api.multi
#     @api.depends('budget_planned_amount')
#     def _get_budget(self):
#         for record in self:
#             if record.account_id:
#                 budget_total = 0
#                 for budget in record.account_id.crossovered_budget_line:
#                     if budget.planned_amount:
#                         budget_total += budget.planned_amount
#                 record.budget_planned_amount = budget_total

    @api.onchange('account_id')
    def onchange_account_id(self):
        for record in self:
            if record.account_id:
                budget_total = 0
                for budget in record.account_id.crossovered_budget_line:
                    if budget.planned_amount:
                        budget_total += budget.planned_amount
                record.budget_planned_amount = budget_total



class account_analytic_account(models.Model):
    _inherit = 'account.analytic.account'

    @api.multi
    def write(self,vals):
        res = super(account_analytic_account, self).write(vals)
        if 'crossovered_budget_line' in vals:
            for record in self:
                account_analytic_line = self.env['account.analytic.line'].search([('account_id','=',record.id)])
                if account_analytic_line:
                    budget_total = 0
                    for budget in record.crossovered_budget_line:
                        if budget.planned_amount:
                            budget_total += budget.planned_amount
                    for account_line in account_analytic_line:
                        self._cr.execute("UPDATE account_analytic_line SET budget_planned_amount = %s WHERE id = %s",(budget_total,account_line.id))
        return res
