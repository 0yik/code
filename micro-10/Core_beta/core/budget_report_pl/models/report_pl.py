# -*- coding: utf-8 -*-
from odoo import fields, models, api
from datetime import datetime
import calendar
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.tools import ustr

class BudgetReportPL(models.Model):
    _name = "budget.report.pl"
    _description = "Budget Report P&L"
    _inherit = ['mail.thread']
    _order = 'id desc'

    name = fields.Char('Budget Name')
    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self.env.user)
    date_from = fields.Date('Start Date')
    date_to = fields.Date('End Date')
    line_ids = fields.One2many('budget.report.pl.line', 'budget_id', 'Budget Lines')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('cancel', 'Cancelled'),
        ('confirm', 'Confirmed'),
        ('validate', 'Validated'),
        ('done', 'Done')
    ], 'Status', default='draft', index=True, required=True, readonly=True, copy=False, track_visibility='always')

    @api.multi
    def action_budget_confirm(self):
        self.write({'state': 'confirm'})

    @api.multi
    def action_budget_draft(self):
        self.write({'state': 'draft'})

    @api.multi
    def action_budget_validate(self):
        self.write({'state': 'validate'})

    @api.multi
    def action_budget_cancel(self):
        self.write({'state': 'cancel'})

    @api.multi
    def action_budget_done(self):
        self.write({'state': 'done'})

BudgetReportPL()

class BudgetReportPLLine(models.Model):
    _name = "budget.report.pl.line"
    _description = "Budget Report P&L Lines"
    _order = 'sequence'

    sequence = fields.Integer(default=10, help="Gives the sequence of this line.")
    budget_id = fields.Many2one('budget.report.pl', 'Budget')
    account_id = fields.Many2one('account.account', 'Account')
    date_from = fields.Date('Start Date')
    date_to = fields.Date('End Date')
    paid_date = fields.Date('Paid Date')
    planned_amount = fields.Float('Planned Amount', required=True, digits=0)
    theoretical_amount = fields.Float('Theoretical Amount', required=True, digits=0)
    practical_amount = fields.Float(compute='_compute_practical_amount', string='Practical Amount', digits=0)
    last_month_practical_amount = fields.Float(compute='_compute_last_month_practical_amount', string='Practical Amount', digits=0)
    last_year_practical_amount = fields.Float(compute='_compute_last_year_practical_amount', string='Practical Amount', digits=0)
    this_year_practical_amount = fields.Float(compute='_compute_this_year_practical_amount', string='Practical Amount', digits=0)
    percentage = fields.Float(compute='_compute_percentage', string='Achievement')
    company_id = fields.Many2one(related='budget_id.company_id', comodel_name='res.company', string='Company', store=True, readonly=True)

    @api.multi
    @api.depends('date_from', 'date_to', 'account_id')
    def _compute_practical_amount(self):
        for line in self:
            result = 0.0
            date_to = self.env.context.get('wizard_date_to') or line.date_to
            date_from = self.env.context.get('wizard_date_from') or line.date_from
            if line.account_id.id:
                self.env.cr.execute("""
                    SELECT SUM(debit)-SUM(credit)
                    FROM account_move_line
                    WHERE account_id=%s
                    AND (date between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))""",
                    (line.account_id.id, date_from, date_to))
                result = self.env.cr.fetchone()[0] or 0.0
            line.practical_amount = result

    @api.multi
    @api.depends('date_from', 'date_to', 'account_id')
    def _compute_last_month_practical_amount(self):
        for line in self:
            result = 0.0
            date_from = datetime.strptime(line.date_from, "%Y-%m-%d")
            date_from = date_from - relativedelta(months=1)
            date_from = date_from.replace(day=1)
            date_to = date_from
            date_to = date_to.replace(day=calendar.monthrange(date_from.year, date_from.month)[1])
            date_from = str(date_from.date())
            date_to = str(date_to.date())
            if line.account_id.id:
                self.env.cr.execute("""
                    SELECT SUM(debit)-SUM(credit)
                    FROM account_move_line
                    WHERE account_id=%s
                    AND (date between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))""",
                    (line.account_id.id, date_from, date_to))
                result = self.env.cr.fetchone()[0] or 0.0
            line.last_month_practical_amount = result

    @api.multi
    @api.depends('date_from', 'date_to', 'account_id')
    def _compute_last_year_practical_amount(self):
        for line in self:
            result = 0.0
            date_from = datetime.strptime(line.date_from, "%Y-%m-%d")
            date_from = date_from.replace(day=1, month=1, year=date_from.year-1)
            date_to = date_from.replace(day=31, month=12, year=date_from.year-1)
            date_from = str(date_from.date())
            date_to = str(date_to.date())
            if line.account_id.id:
                self.env.cr.execute("""
                    SELECT SUM(debit)-SUM(credit)
                    FROM account_move_line
                    WHERE account_id=%s
                    AND (date between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))""",
                    (line.account_id.id, date_from, date_to))
                result = self.env.cr.fetchone()[0] or 0.0
            line.last_year_practical_amount = result

    @api.multi
    @api.depends('date_from', 'date_to', 'account_id')
    def _compute_this_year_practical_amount(self):
        for line in self:
            result = 0.0
            date_from = datetime.strptime(line.date_from, "%Y-%m-%d")
            date_from = date_from.replace(day=1, month=1)
            date_to = date_from.replace(day=31, month=12)
            date_from = str(date_from.date())
            date_to = str(date_to.date())
            if line.account_id.id:
                self.env.cr.execute("""
                    SELECT SUM(debit)-SUM(credit)
                    FROM account_move_line
                    WHERE account_id=%s
                    AND (date between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))""",
                    (line.account_id.id, date_from, date_to))
                result = self.env.cr.fetchone()[0] or 0.0
            line.this_year_practical_amount = result

    @api.multi
    @api.depends('practical_amount', 'theoretical_amount')
    def _compute_percentage(self):
        for line in self:
            if line.theoretical_amount != 0.00:
                line.percentage = float((line.practical_amount or 0.0) / line.theoretical_amount) * 100
            else:
                line.percentage = 0.00

BudgetReportPLLine()