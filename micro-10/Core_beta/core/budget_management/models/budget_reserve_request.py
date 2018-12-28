# -*- coding: utf-8 -*-
from odoo import api, fields, models,_
from datetime import datetime
from odoo.exceptions import UserError

class BudgetReserveRequest(models.Model):
    _name = 'budget.reserve.request'

    name = fields.Char('Budget Reserve Reference')
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
    reserver_for_all = fields.Boolean('Reserver For All')
    date_from = fields.Date('Period Date From')
    date_to = fields.Date('Period Date To')

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('budget.reserve.sequence')
        result = super(BudgetReserveRequest, self).create(vals)
        return result

    @api.multi
    def submit_for_approval(self):
        for rec1 in self:
            rec1.state = 'waiting_for_approval'
            if rec1.crossovered_budget_id:
                if not rec1.reserver_for_all:
                    for line in rec1.crossovered_budget_id.crossovered_budget_line:
                        if line.analytic_account_id.id == rec1.analytic_account_id.id:
                            # line.reserved_amount += rec1.reserve_budget
                            if line.reserved_amount + rec1.reserve_budget > line.planned_amount:
                                raise UserError(
                                    _("Reserve amount can not exceed Planned Amount. Please revise Budget Reserve"))
                else:
                    list_suitbale_aa = self.env['crossovered.budget.lines'].search([
                        ('date_from','<=',rec1.budget_reserve_date),
                        ('date_to','>=',rec1.budget_reserve_date)
                    ])
                    if any([aa.planned_amount > aa.reserved_amount + rec1.reserve_budget for aa in list_suitbale_aa]):
                        raise UserError(_("Planned Amount can not exceed Budget Reserve. Please revise Budget Reserve"))
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
        # for rec1 in self.env['budget.reserve.request'].search([('analytic_account_id','=',self.analytic_account_id.id)]):
        for rec1 in self:
                rec1.analytic_account_id.budget_reserver_ids = [(4, self.id)]
        return True
