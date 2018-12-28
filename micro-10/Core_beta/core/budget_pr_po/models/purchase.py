# -*- coding: utf-8 -*-
from odoo import api, fields, models,_
from datetime import datetime
from odoo.exceptions import UserError

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.depends('product_id', 'account_analytic_id')
    @api.multi
    def _caluculate_butget_amount(self):
        for line in self:
            if line.account_analytic_id and line.product_id:
                for budget_line in line.account_analytic_id.product_budget_lines:
                    group_product = budget_line.group_product_id
                    prod_list = map(int,group_product.product_ids)
                    if line.product_id.id in prod_list:
                        line.remaining_budget = budget_line.balance_left
                        line.budgeted_amount = budget_line.planned_amount


    budgeted_amount = fields.Float(compute='_caluculate_butget_amount', string='Budgeted Amount')
    remaining_budget = fields.Float(compute='_caluculate_butget_amount', string='Remaining Budget')
