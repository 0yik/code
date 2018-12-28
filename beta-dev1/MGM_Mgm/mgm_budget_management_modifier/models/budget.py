# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class CrossoveredBudgetLinesInherit(models.Model):
    _inherit = "crossovered.budget.lines"

    reserved_amount = fields.Float(string="Reserved Amount", copy=False)

class BudgetReserveRequest(models.Model):
    _inherit = 'budget.reserve.request'

    @api.multi
    def approve(self):
        for rec in self:
            planned_amount = sum(rec.analytic_account_id.crossovered_budget_line.mapped('planned_amount'))
            if planned_amount < rec.reserve_budget:
                raise ValidationError('The Planned Amount should be more then the Reserved Amount. Please revise your budget')
        res = super(BudgetReserveRequest, self).approve()
        return res

