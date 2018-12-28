# -*- coding: utf-8 -*-
from odoo import api, fields, models,_
from datetime import datetime
from odoo.exceptions import UserError

class AnalyticBudgetReserveRequest(models.Model):
    _name = 'analytic.budget.reserve.request'

    name = fields.Char('Analytic Budget Reserve Reference')
    requester = fields.Many2one('res.users', string='Requester')
    crossovered_budget_id = fields.Many2one('crossovered.budget', 'Budget')
    budget_reserve_date = fields.Date(string='Date', default=datetime.now().date())
    analytic_account_id = fields.Many2one('account.analytic.account', string="Analytic Account")
    reserve_budget = fields.Float(string="Reserve Budget")
    reason = fields.Text(string="Reason")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_for_approval', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled')
    ], 'Status', default='draft', index=True, required=True, readonly=True, copy=False, track_visibility='always')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('analytic.budget.reserve.sequence')
        result = super(AnalyticBudgetReserveRequest, self).create(vals)
        return result

    @api.multi
    def submit_for_approval(self):
        for rec in self:
            rec.state = 'waiting_for_approval'
        return True

    @api.multi
    def submit_for_reject(self):
        for rec in self:
            rec.state = 'rejected'
        return True

    @api.multi
    def set_to_cancel(self):
        for rec in self:
            rec.state = 'cancelled'
        return True

    @api.multi
    def approve(self):
        self.state = 'approved'
#         for rec1 in self.env['analytic.budget.reserve.request'].search([('analytic_account_id', '=', self.analytic_account_id.id)]):
#             if rec1.state == 'approved' and rec1.crossovered_budget_id:
#                 for line in rec1.crossovered_budget_id.crossovered_budget_line:
#                     if line.analytic_account_id.id == rec1.analytic_account_id.id:
#                         line.reserved_amount += rec1.reserve_budget
        return True
