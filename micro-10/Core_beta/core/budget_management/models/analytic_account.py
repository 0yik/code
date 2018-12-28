# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError


class AnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.depends('crossovered_budget_line.reserved_amount')
    def _compute_reserve_amount(self):
        for record in self:
            record.reserved_amount = sum([line.reserved_amount for line in record.crossovered_budget_line])
            record.planned_amount = sum([line.planned_amount for line in record.crossovered_budget_line])

    reserved_amount = fields.Float(compute='_compute_reserve_amount', string='Reserved Amount')
    planned_amount = fields.Float(compute='_compute_reserve_amount', string='Reserved Amount')
    budget_allocation_ids = fields.Many2many('budget.allocation.request', string='Budget Allocation Request')
    budget_reserver_ids = fields.Many2many('budget.reserve.request', string='Budget Reservation Request')

    @api.multi
    def write(self, vals):
        res = super(AnalyticAccount, self).write(vals)
        module = self.env['ir.module.module'].search([
            ('name', '=', 'mgm_budget_management_modifier')
        ])
        if module and module.state != 'installed':
            """ added condition for not run below code if 
            'mgm_budget_management_modifier' module is installed.
             if that module is not installed then run below code """

            for rec in self:
                if sum(rec.crossovered_budget_line.mapped('planned_amount')) < rec.reserved_amount:
                    raise ValidationError(
                        'The Reserved Amount has exceeded the Planned Amount. Please revise your budget')

        return res

    @api.onchange('crossovered_budget_line')
    def onchange_crossovered_budget_line(self):
        if self.crossovered_budget_line:
            if sum(self.crossovered_budget_line.mapped('planned_amount')) < self.reserved_amount:
                raise ValidationError('The Reserved Amount has exceeded the Planned Amount. Please revise your budget')
                # # self.crossovered_budget_line = [(6, 0, self.crossovered_budget_line.ids)]
                # return {'warning': warning}



AnalyticAccount()


class CrossOveredBudgetLines(models.Model):
    _inherit = 'crossovered.budget.lines'

    reserved_amount = fields.Float('Reserved Amount')

    # @api.onchange('planned_amount')
    # def onchange_planned_amount(self):
    #     if self.analytic_account_id:
    #         warning = {}
    #         if self.planned_amount + self.analytic_account_id.planned_amount > self.analytic_account_id.reserved_amount:
    #             self.planned_amount = 0
    #             warning = {'title': 'Value Error!', 'message': 'The Planned Amount has exceeded the Reserved Amount. Please revise your budget'}
    #         return {'warning': warning}


CrossOveredBudgetLines()