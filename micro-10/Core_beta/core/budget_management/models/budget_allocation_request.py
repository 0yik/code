# -*- coding: utf-8 -*-
from odoo import api, fields, models
from datetime import datetime

class BudgetAllocationRequest(models.Model):
    _name = 'budget.allocation.request'
    _inherit = 'mail.thread'
    _description = 'Budget Allocation Request'
    _order = 'id desc'

    name = fields.Char('Budget Allocation Reference')
    requester_id = fields.Many2one('res.users', string='Requester')
    date = fields.Date('Date', default=datetime.now().date())
    budget_id = fields.Many2one('crossovered.budget', 'Budget')
    budget_position_id = fields.Many2one('account.budget.post', 'Budget position')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    reserve_budget = fields.Float('Reserve Budget')
    reason = fields.Text(string="Reason")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_for_approval', 'Waiting for Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled')
    ], 'Status', default='draft', index=True, track_visibility='always')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('budget.allocation.sequence')
        result = super(BudgetAllocationRequest, self).create(vals)
        return result

    @api.multi
    def submit_for_approval(self):
        self.write({'state': 'waiting_for_approval'})

    @api.multi
    def button_cancel(self):
        self.write({'state': 'cancelled'})

    @api.multi
    def button_approve(self):
        budget_line_ids = self.env['crossovered.budget.lines'].search([('crossovered_budget_id','=',self.budget_id.id),('general_budget_id','=',self.budget_position_id.id)])
        for line in budget_line_ids:
            line.reserved_amount = line.reserved_amount + self.reserve_budget
        self.analytic_account_id.budget_allocation_ids = [(4, self.id)]
        self.write({'state': 'approved'})

    @api.multi
    def button_reject(self):
        self.write({'state': 'rejected'})

BudgetAllocationRequest()