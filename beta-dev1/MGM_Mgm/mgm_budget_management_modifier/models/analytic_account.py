# -*- coding: utf-8 -*-
from odoo import api, fields, models
from odoo.exceptions import ValidationError

class AnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    @api.multi
    def write(self, vals):
        res = super(AnalyticAccount, self).write(vals)
        for rec in self:
            planned_amount = sum(rec.crossovered_budget_line.mapped('planned_amount'))
            if planned_amount < rec.reserved_amount:
                raise ValidationError('The Planned Amount should be more then the Reserved Amount. Please revise your budget')
        return res
