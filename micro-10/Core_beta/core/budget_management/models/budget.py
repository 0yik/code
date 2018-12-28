# -*- coding: utf-8 -*-
from odoo import api, fields, models,_
from datetime import datetime
from odoo.exceptions import UserError


class CrossoveredBudget(models.Model):
    _inherit = 'crossovered.budget'

    # state = fields.Selection(selection_add=[("waiting_for_approval", "Waiting for Approval"),
    #                       ("rejected", "Rejected")])
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_for_approval', 'Waiting for Approval'),
        ('cancel', 'Cancelled'),
        ('confirm', 'Confirmed'),
        ('validate', 'Validated'),
        ('done', 'Done'),
        ('rejected', 'Rejected')
    ], 'Status', default='draft', index=True, required=True, readonly=True, copy=False, track_visibility='always')
    budget_change_history_line = fields.One2many('budget.change.history', 'crossovered_budget_id', 'Budget Lines', copy=True)

    @api.multi
    def check_validation(self):
        for rec in self:
            date_from = rec.date_from
            date_to = rec.date_to
            query = "select id from crossovered_budget " \
                    "where state in ('validate') and " \
                    "(((date_from between '" + date_from + "' and '" + date_to + "') or " \
                    "(date_to between '" + date_from + "' and '" + date_to + "')) or " \
                    "(date_from = '" + date_from + "' and date_to = '" + date_to + "') or " \
                    "('" + date_from + "' between date_from and date_to))"
            self._cr.execute(query)
            existing_ids = [x[0] for x in self._cr.fetchall()]

            if rec.id in existing_ids:
                existing_ids.remove(rec.id)
            if existing_ids:
                raise UserError(_('There is another budget for the same period.'))

    @api.multi
    def submit_for_approval(self):
        for rec in self:
            rec.state = 'waiting_for_approval'
        return True

    @api.multi
    def approve_budget(self):
        for rec in self:
            rec.check_validation()
            rec.state = 'validate'
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
    def run_budget_done(self):
        search_old_budgets = self.env['crossovered.budget'].sudo().search([
            ('date_to', '<', datetime.now().date()),('state','=','validate')
        ])
        if search_old_budgets:
            search_old_budgets.write({
                'state': 'done'
            })
        return True


class CrossoveredBudgetLinesInherit(models.Model):
    _inherit = "crossovered.budget.lines"

    reserved_amount = fields.Float(string="Reserved Amount", compute="_compute_reserve_amount")

    @api.multi
    def check_already_lines(self):
        for rec in self:
            date_from = rec.date_from
            date_to = rec.date_to
            if rec.analytic_account_id and rec.general_budget_id:
                query = "select id from crossovered_budget_lines " \
                        "where general_budget_id in (" + str(rec.general_budget_id.id) + ") and " \
                        "analytic_account_id in (" + str(rec.analytic_account_id.id) + ") and " \
                        "crossovered_budget_id in (" + str(rec.crossovered_budget_id.id) + ") and " \
                        "(((date_from between '" + date_from + "' and '" + date_to + "') or "\
                        "(date_to between '" + date_from + "' and '" + date_to + "')) or " \
                        "(date_from = '" + date_from + "' and date_to = '" + date_to + "') or " \
                        "('" + date_from + "' between date_from and date_to))"
                self._cr.execute(query)
                existing_ids = [x[0] for x in self._cr.fetchall()]
                if rec.id in existing_ids:
                    existing_ids.remove(rec.id)
                if existing_ids:
                    raise UserError(_('There is another line for the same period.'))
            elif rec.general_budget_id and not rec.analytic_account_id:
                query = "select id from crossovered_budget_lines " \
                        "where general_budget_id in (" + str(rec.general_budget_id.id) + ") and " \
                        "analytic_account_id is null and " \
                        "crossovered_budget_id in (" + str(rec.crossovered_budget_id.id) + ") and " \
                        "(((date_from between '" + date_from + "' and '" + date_to + "') or " \
                        "(date_to between '" + date_from + "' and '" + date_to + "')) or " \
                        "(date_from = '" + date_from + "' and date_to = '" + date_to + "') or " \
                        "('" + date_from + "' between date_from and date_to))"
                self._cr.execute(query)
                existing_ids = [x[0] for x in self._cr.fetchall()]
                if rec.id in existing_ids:
                    existing_ids.remove(rec.id)
                if existing_ids:
                    raise UserError(_('There is another line for the same period.'))

    @api.model
    def create(self, vals):
        result = super(CrossoveredBudgetLinesInherit, self).create(vals)
        result.check_already_lines()
        return result

    @api.model
    def write(self, vals):
        result = super(CrossoveredBudgetLinesInherit, self).write(vals)
        self.check_already_lines()
        return result

    @api.multi
    def _compute_reserve_amount(self):
        for rec in self:
            BudgetReverse = rec.env['budget.reserve.request']
            domain_budget_reverse = [
                # ('analytic_account_id', '=', rec.analytic_account_id.id),
                ('budget_reserve_date', '>=', rec.date_from),
                ('budget_reserve_date', '<=', rec.date_to),
                ('state', '=', 'approved'),
                ('crossovered_budget_id', '=', rec.crossovered_budget_id.id),
            ]
            reserved_amount = 0
            for rec1 in BudgetReverse.search(domain_budget_reverse):
                if not rec1.reserver_for_all:
                    if rec1.analytic_account_id == rec.analytic_account_id:
                        reserved_amount += rec1.reserve_budget
                        if reserved_amount > rec.planned_amount:
                            raise UserError(
                                _("Reserve amount can not exceed Planned Amount. Please revise Budget Reserve"))
                else:
                    reserved_amount += rec1.reserve_budget
                    if rec.planned_amount > reserved_amount :
                        raise UserError(_("Planned Amount can not exceed Budget Reserve. Please revise Budget Reserve"))

            rec.reserved_amount = reserved_amount

    @api.multi
    def _compute_practical_amount(self):
        for line in self:
            result = 0.0
            acc_ids = line.general_budget_id.account_ids.ids
            if not acc_ids:
                raise UserError(_("The Budget '%s' has no accounts!") % ustr(line.general_budget_id.name))
            date_to = self.env.context.get('wizard_date_to') or line.date_to
            date_from = self.env.context.get('wizard_date_from') or line.date_from
            if line.analytic_account_id.id:
                self.env.cr.execute("""
                        SELECT SUM(amount)
                        FROM account_analytic_line
                        WHERE account_id=%s
                            AND (date between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))
                            AND general_account_id=ANY(%s)""",
                                    (line.analytic_account_id.id, date_from, date_to, acc_ids,))
                result = self.env.cr.fetchone()[0] or 0.0
            else:
                self.env.cr.execute("""
                                        SELECT SUM(amount)
                                        FROM account_analytic_line
                                        WHERE 
                                            (date between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))
                                            AND general_account_id=ANY(%s)""",
                                    ( date_from, date_to, acc_ids,))
                result = self.env.cr.fetchone()[0] or 0.0
            line.practical_amount = result

class BudgetChangeHistory(models.Model):
    _name = 'budget.change.history'

    crossovered_budget_id = fields.Many2one('crossovered.budget', 'Budget', ondelete='cascade', index=True)
    general_budget_id = fields.Many2one('account.budget.post', 'Budgetary Position')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    date_changed = fields.Date('Date Changed')
    old_planned_amount = fields.Float('Old Planned Amount', digits=0)
    new_planned_amount = fields.Float('New Planned Amount', digits=0)
    requester = fields.Many2one('res.users', string='Requester')
    approver = fields.Many2one('res.users', string='Approver')

