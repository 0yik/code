# -*- coding: utf-8 -*-
from odoo import api, fields, models,_
from datetime import datetime
from odoo.exceptions import UserError

class BudgetChangeRequest(models.Model):
    _name = 'budget.change.request'

    name = fields.Char('Budget Change Reference')
    requester = fields.Many2one('res.users', string='Requester')
    crossovered_budget_id = fields.Many2one('crossovered.budget', 'Budget')
    budget_change_date = fields.Date(string='Date', default=datetime.now().date())
    crossovered_budget_line = fields.One2many('budget.change.lines', 'budget_change_request_id',
        'Budget Lines', copy=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_for_approval', 'Waiting for Approval'),
        ('confirm', 'Confirmed'),
        ('rejected', 'Rejected')
    ], 'Status', default='draft', index=True, required=True, readonly=True, copy=False, track_visibility='always')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('budget.change.sequence')
        result = super(BudgetChangeRequest, self).create(vals)
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
    def reset_to_draft(self):
        for rec in self:
            rec.state = 'draft'
        return True

    @api.multi
    def approve(self):
        budget_line_obj = self.env['crossovered.budget.lines'].sudo()
        budget_change_history_obj = self.env['budget.change.history'].sudo()
        for rec1 in self:
            rec1.state = 'confirm'
            for rec in rec1.crossovered_budget_line:
                if rec.budget_change_request_id and rec.budget_change_request_id.crossovered_budget_id:
                    analytic_account_id = rec.analytic_account_id and rec.analytic_account_id.id or False
                    budget_lines = budget_line_obj.search([
                        ('crossovered_budget_id', '=', rec.budget_change_request_id.crossovered_budget_id.id),
                        ('general_budget_id', '=', rec.general_budget_id.id),
                        ('analytic_account_id', '=', analytic_account_id)],
                        limit=1, order='id desc')
                    if budget_lines:
                        budget_change_history_obj.create({
                            'crossovered_budget_id': rec.budget_change_request_id.crossovered_budget_id.id,
                            'general_budget_id': rec.general_budget_id.id,
                            'analytic_account_id': rec.analytic_account_id.id,
                            'date_changed': datetime.now().date(),
                            'old_planned_amount': rec.current_planned_amount,
                            'new_planned_amount': rec.new_planned_amount,
                            'requester': rec1.requester and rec1.requester.id or False,
                            'approver': self.env.user and self.env.user.id or False,
                        })
                        budget_lines.planned_amount = rec.new_planned_amount

                    # if rec.general_budget_id and rec.analytic_account_id:
                    #     budget_lines = budget_line_obj.search([
                    #         ('crossovered_budget_id','=',rec.budget_change_request_id.crossovered_budget_id.id),
                    #         ('general_budget_id', '=', rec.general_budget_id.id),
                    #         ('analytic_account_id', '=', rec.analytic_account_id.id)],
                    #         limit=1, order='id desc')
                    #     if budget_lines:
                    #         budget_change_history_obj.create({
                    #             'crossovered_budget_id': rec.budget_change_request_id.crossovered_budget_id.id,
                    #             'general_budget_id': rec.general_budget_id.id,
                    #             'analytic_account_id': rec.analytic_account_id.id,
                    #             'date_changed': datetime.now().date(),
                    #             'old_planned_amount': rec.current_planned_amount,
                    #             'new_planned_amount': rec.new_planned_amount,
                    #         })
                    #         budget_lines.planned_amount = rec.new_planned_amount
                    #
                    # if rec.general_budget_id and not rec.analytic_account_id:
                    #     budget_lines = budget_line_obj.search([
                    #         ('crossovered_budget_id', '=', rec.budget_change_request_id.crossovered_budget_id.id),
                    #         ('general_budget_id', '=', rec.general_budget_id.id),
                    #         ('analytic_account_id', '=', False)],
                    #         limit=1, order='id desc')
                    #     if budget_lines:
                    #         budget_change_history_obj.create({
                    #             'crossovered_budget_id': rec.budget_change_request_id.crossovered_budget_id.id,
                    #             'general_budget_id': rec.general_budget_id.id,
                    #             'analytic_account_id': rec.analytic_account_id.id,
                    #             'date_changed': datetime.now().date(),
                    #             'old_planned_amount': rec.current_planned_amount,
                    #             'new_planned_amount': rec.new_planned_amount,
                    #         })
                    #         budget_lines.planned_amount = rec.new_planned_amount
        return True


class BudgetChangeLines(models.Model):
    _name = "budget.change.lines"
    _description = "Budget Line"

    @api.multi
    @api.depends('general_budget_id', 'analytic_account_id', 'budget_change_request_id.crossovered_budget_id')
    def _get_current_planned_amount(self):
        for rec in self:
            amount = 0.00
            budget_line_obj = self.env['crossovered.budget.lines'].sudo()
            if rec.budget_change_request_id and rec.budget_change_request_id.crossovered_budget_id:
                analytic_account_id = rec.analytic_account_id and rec.analytic_account_id.id or False
                budget_lines = budget_line_obj.search([
                    ('crossovered_budget_id', '=', rec.budget_change_request_id.crossovered_budget_id.id),
                    ('general_budget_id', '=', rec.general_budget_id.id),
                    ('analytic_account_id', '=', analytic_account_id)],
                    limit=1, order='id desc')
                if budget_lines:
                    amount = budget_lines.planned_amount
                # if rec.general_budget_id and rec.analytic_account_id:
                #     budget_lines = budget_line_obj.search([
                #         ('crossovered_budget_id','=',rec.budget_change_request_id.crossovered_budget_id.id),
                #         ('general_budget_id', '=', rec.general_budget_id.id),
                #         ('analytic_account_id', '=', rec.analytic_account_id.id)],
                #         limit=1, order='id desc')
                #     if budget_lines:
                #         amount = budget_lines.planned_amount
                #
                # if rec.general_budget_id and not rec.analytic_account_id:
                #     budget_lines = budget_line_obj.search([
                #         ('crossovered_budget_id', '=', rec.budget_change_request_id.crossovered_budget_id.id),
                #         ('general_budget_id', '=', rec.general_budget_id.id),
                #         ('analytic_account_id', '=', False)],
                #         limit=1, order='id desc')
                #     if budget_lines:
                #         amount = budget_lines.planned_amount
            rec.current_planned_amount = amount

    # @api.multi
    # @api.onchange('general_budget_id', 'analytic_account_id')
    # def onchange_planned_amount(self):
    #     for rec in self:
    #         amount = 0.00
    #         budget_line_obj = self.env['crossovered.budget.lines'].sudo()
    #         if rec.budget_change_request_id and rec.budget_change_request_id.crossovered_budget_id:
    #             analytic_account_id = rec.analytic_account_id and rec.analytic_account_id.id or False
    #             budget_lines = budget_line_obj.search([
    #                 ('crossovered_budget_id', '=', rec.budget_change_request_id.crossovered_budget_id.id),
    #                 ('general_budget_id', '=', rec.general_budget_id.id),
    #                 ('analytic_account_id', '=', analytic_account_id)],
    #                 limit=1, order='id desc')
    #             if budget_lines:
    #                 amount = budget_lines.planned_amount
    #         rec.current_planned_amount = amount

    budget_change_request_id = fields.Many2one('budget.change.request', 'Budget change Request', ondelete='cascade', index=True)
    # crossovered_budget_id = fields.Many2one(related='budget_change_request_id.crossovered_budget_id')
    general_budget_id = fields.Many2one('account.budget.post', 'Budgetary Position')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    current_planned_amount = fields.Float('Current Planned Amount', digits=0, compute='_get_current_planned_amount')
    # current_planned_amount = fields.Float('Current Planned Amount', digits=0)
    new_planned_amount = fields.Float('New Planned Amount', digits=0)
