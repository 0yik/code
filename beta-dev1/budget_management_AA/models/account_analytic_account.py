from odoo import api, fields, models,_
from datetime import datetime
from odoo.exceptions import UserError
from odoo.tools import ustr

class Budgetlines(models.Model):
    _inherit = 'crossovered.budget.lines'

    @api.model
    def create(self, vals):
        res = super(Budgetlines, self).create(vals)
        if res.analytic_account_id:
            res.analytic_account_id.date_from = res.crossovered_budget_id.date_from
            res.analytic_account_id.date_to = res.crossovered_budget_id.date_to
            res.analytic_account_id.financial_budget_number = res.crossovered_budget_id
        return res

    @api.multi
    def write(self, vals):
        for rec in self:
            if 'analytic_account_id' in vals:
                if rec.analytic_account_id:
                    rec.analytic_account_id.date_from = False
                    rec.analytic_account_id.date_to = False
                    rec.analytic_account_id.financial_budget_number = False
        res = super(Budgetlines, self).write(vals)
        for rec in self:
            rec.analytic_account_id.date_from = rec.crossovered_budget_id.date_from
            rec.analytic_account_id.date_to = rec.crossovered_budget_id.date_to
            rec.analytic_account_id.financial_budget_number = rec.crossovered_budget_id
        return res



class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    financial_budget_number = fields.Many2one('crossovered.budget', string='Financial Budget Number')
    # parent_id = fields.Many2one('account.analytic.account', string='Parent')
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    use_budget = fields.Boolean('Budget')
    division_aa_lines = fields.One2many('division.aa.lines', 'aa_id')

    planned_amount = fields.Float('Planned Amount',digits=0 , readonly=0, compute=False)

    practical_amount = fields.Float( string='Practical Amount', digits=0, compute="_compute_amount_practical", store=False)
    practical_amount_without_child = fields.Float( string='Practical Amount', digits=0, compute="_compute_amount")
    theoritical_amount = fields.Float( string='Theoretical Amount', digits=0, compute="_compute_amount")

    reserved_amount = fields.Float(string="Reserved Amount", compute="_compute_amount" )
    allocation_amount = fields.Float("Allocation Amount", compute="_compute_amount")
    achievement = fields.Float("Achievement")
    child_ids =  fields.One2many('account.analytic.account','parent_id')
    allow_over_limit = fields.Boolean('Allow Over Limit')

    def get_parent(self):
        if self.parent_id:
            return self.parent_id.get_parent()
        else:
            return self

    def get_parent_budget(self):
        parent_id = self.get_parent()
        domain = [
            ('analytic_account_id', '=', parent_id.id),
            ('date_from', '<=', parent_id.date_from),
            ('date_to', '>=', parent_id.date_to),
            ('crossovered_budget_id.state', '=', 'validate'),
            ('crossovered_budget_id', '=', parent_id.financial_budget_number.id),
        ]
        BudgetLine = self.env['crossovered.budget.lines']
        return BudgetLine.search(domain)

    @api.multi
    def get_theorical_amount(self):
        today = fields.Datetime.now()
        for line in self:
            theo_amt = 0
            budget = line.get_parent_budget()
            if budget:
                if budget.paid_date:
                    if fields.Datetime.from_string(budget.date_to) <= fields.Datetime.from_string(budget.paid_date):
                        theo_amt = 0.00
                    else:
                        theo_amt = line.planned_amount
                else:
                    line_timedelta = fields.Datetime.from_string(budget.date_to) - fields.Datetime.from_string(
                        budget.date_from)
                    elapsed_timedelta = fields.Datetime.from_string(today) - (
                    fields.Datetime.from_string(budget.date_from))

                    if elapsed_timedelta.days < 0:
                        theo_amt = 0.00
                    elif line_timedelta.days > 0 and fields.Datetime.from_string(today) < fields.Datetime.from_string(
                            budget.date_to):
                        theo_amt = (
                                   elapsed_timedelta.total_seconds() / line_timedelta.total_seconds()) * line.planned_amount
                    else:
                        theo_amt = line.planned_amount

            return theo_amt

    @api.depends('child_ids','line_ids')
    @api.multi
    def _compute_amount_practical(self):
        for rec in self:
            practical_amount = rec.get_practical_amount()
            for line in rec.child_ids:
                practical_amount += line.get_practical_amount()
            rec.practical_amount = practical_amount

    def get_practical_amount(self):
        for line in self:
            date_to = self.env.context.get('wizard_date_to') or line.date_to
            date_from = self.env.context.get('wizard_date_from') or line.date_from
            if line.id:
                self.env.cr.execute("""
                        SELECT SUM(amount)
                        FROM account_analytic_line
                        WHERE account_id=%s
                            AND (date between to_date(%s,'yyyy-mm-dd') AND to_date(%s,'yyyy-mm-dd'))
                           """,
                                    (line.id, date_from, date_to))
                result = self.env.cr.fetchone()[0] or 0.0

                return result

    @api.multi
    def _compute_amount(self):
        for rec in self:
            id = rec.id
            BudgetLine = rec.env['crossovered.budget.lines']
            domain_budget_line = [
                ('analytic_account_id', '=', id),
                ('date_from', '<=', rec.date_from),
                ('date_to', '>=', rec.date_to),
                ('crossovered_budget_id.state', '=', 'validate'),
                ('crossovered_budget_id', '=', rec.financial_budget_number.id),
            ]
            BudgetReverse = rec.env['budget.reserve.request']
            domain_budget_reverse = [
                ('analytic_account_id', '=', id),
                ('budget_reserve_date', '>=', rec.date_from),
                ('budget_reserve_date', '<=', rec.date_to),
                ('state', '=', 'approved'),
                ('crossovered_budget_id', '=', rec.financial_budget_number.id),
            ]
            BudgetAllocation = rec.env['budget.analytic.account.allocation']
            domain_budget_allocation = [
                ('analytic_account_id', '=', id),
                ('date', '>=', rec.date_from),
                ('date', '<=', rec.date_to),
                ('state', '=', 'approved'),
                ('budget_id', '=', rec.financial_budget_number.id),
            ]
            allocation_amount = reserved_amount  = theoritical_amount = 0
            if not rec.parent_id and len(BudgetLine.search(domain_budget_line)) >= 1:
                for line in BudgetLine.search(domain_budget_line):
                    theoritical_amount += line.theoritical_amount
            else:
                if rec.planned_amount:
                    theoritical_amount = rec.get_theorical_amount()


            for line in BudgetReverse.search(domain_budget_reverse):
                reserved_amount += line.reserve_budget
            for line in BudgetAllocation.search(domain_budget_allocation):
                allocation_amount += line.allocation_budget

            rec.allocation_amount = allocation_amount
            rec.reserved_amount = reserved_amount
            rec.theoritical_amount = theoritical_amount
            if rec.reserved_amount > rec.planned_amount:
                raise UserError(
                    'The Reserved Amount has exceeded the Planned Amount. Please revise your budget')

    @api.onchange('date_from','date_to','financial_budget_number')
    def onchange_amount(self):
        if self.date_from and self.date_to and self.financial_budget_number and self._origin:
            id = self._origin.id
            rec = self
            BudgetLine = rec.env['crossovered.budget.lines']
            domain_budget_line = [
                ('analytic_account_id','=',id),
                ('date_from','<=',rec.date_from),
                ('date_to','>=',rec.date_to),
                ('crossovered_budget_id.state', '=', 'validate'),
                ('crossovered_budget_id','=',rec.financial_budget_number.id),
            ]
            BudgetReverse = rec.env['budget.reserve.request']
            domain_budget_reverse= [
                ('analytic_account_id', '=', id),
                ('budget_reserve_date', '>=', rec.date_from),
                ('budget_reserve_date', '<=', rec.date_to),
                ('state', '=', 'approved'),
                ('crossovered_budget_id', '=', rec.financial_budget_number.id),
            ]
            BudgetAllocation = rec.env['budget.analytic.account.allocation']
            domain_budget_allocation = [
                ('analytic_account_id', '=', id),
                ('date', '>=', rec.date_from),
                ('date', '<=', rec.date_to),
                ('state', '=', 'approved'),
                ('budget_id', '=', rec.financial_budget_number.id),
            ]
            allocation_amount=reserved_amount=planned_amount = practical_amount = theoritical_amount = 0
            for line in BudgetLine.search(domain_budget_line):
                planned_amount += line.planned_amount
                practical_amount += line.practical_amount
                theoritical_amount += line.theoritical_amount

            for line in BudgetReverse.search(domain_budget_reverse):
                reserved_amount += line.reserve_budget
            for line in BudgetAllocation.search(domain_budget_allocation):
                allocation_amount += line.allocation_budget

            rec.allocation_amount = allocation_amount
            rec.reserved_amount = reserved_amount
            rec.planned_amount = planned_amount
            rec.practical_amount = practical_amount
            rec.theoritical_amount = theoritical_amount



    @api.multi
    def show_popup(self):
        aa_wizard = self.child_ids.mapped('aa_wizard_id')
        if not aa_wizard:
            vals ={
                'date_from': self.date_from,
                'use_budget': self.use_budget,
                'date_to': self.date_to,
                'type': self.type,
                'financial_budget_number': self.financial_budget_number.id,
                'analytic_account_id' : self.id,
                'planned_amount' : self.planned_amount,
            }
            aa_wizard = self.env['aa.wizard'].create(vals)
            if aa_wizard:
                self.child_ids.write({
                    'aa_wizard_id' : aa_wizard.id,
                })

        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            # 'view_id': False,
            'res_model': 'aa.wizard',
            # 'views': [(division_tree_view, 'tree')],
            'view_id': self.env.ref('budget_management_AA.view_division_aa_dept_wizard').id,
            'target': 'new',
            'res_id' : aa_wizard.id,
            'context' : {'default_date_from': self.date_from,'default_use_budget': self.use_budget,'default_date_to': self.date_to, 'default_type': self.type},
        }

    aa_wizard_id = fields.Many2one('aa.wizard')

class AccountAnalyticWiazd(models.Model):
    _name = 'aa.wizard'

    # @api.model
    # def _get_default_line(self):
    #     context = self._context
    #     MODEL = context.get('active_model', False)
    #     ID = context.get('active_id', False)
    #     employee_id = False
    #
    #     return line_ids

    aa_ids = fields.One2many('account.analytic.account', 'aa_wizard_id')
    analytic_account_id = fields.Many2one('account.analytic.account')
    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    use_budget = fields.Boolean('Budget')
    financial_budget_number = fields.Many2one('crossovered.budget', string='Financial Budget Number')
    planned_amount = fields.Float('Planned Amount',digits=0 , readonly=0, compute=False)

    type = fields.Selection([
        ('view', 'Analytic View'),
        ('normal', 'Analytic Account'),
        ('contract', 'Contract or Project'),
        ('template', 'Template of Contract')
    ], 'Type of Account')




class Division_AA_lines(models.Model):
    _name = 'division.aa.lines'

    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    aa_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    from_date = fields.Date(default=datetime.now().date(), string="Start Date")
    to_date = fields.Date(string="End Date")
    planned_amount = fields.Float("Planned Amount")
    reserved_amount = fields.Float("Reserved Amount")
    allocation_amount = fields.Float("Allocation Amount")
    practical_amount = fields.Float("Practical Amount")
    theoritical_amount = fields.Float("Theoritical Amount")
    achievement = fields.Float("Achievement")
    # sub_dept_ids = fields.One2many('sub.dept.descendant.line', 'budget_aa_line_id', string='Sub-Dept')

    @api.model
    def create(self, vals):
        res = super(Division_AA_lines,self).create(vals)
        if res.analytic_account_id:
            res.analytic_account_id.parent_id = res.aa_id
        return res

    @api.onchange('analytic_account_id')
    def onchange_analytic_account_id(self):
        if self.analytic_account_id:
            self.allocation_amount = self.analytic_account_id.allocation_amount
            self.reserved_amount = self.analytic_account_id.reserved_amount
            self.planned_amount = self.analytic_account_id.planned_amount
            self.practical_amount = self.analytic_account_id.practical_amount
            self.theoritical_amount = self.analytic_account_id.theoritical_amount

    @api.multi
    def write(self, vals):
        for rec in self:
            if 'analytic_account_id' in vals:
                if rec.analytic_account_id:
                    rec.analytic_account_id.parent_id = False
        res = super(Division_AA_lines, self).write(vals)
        for rec in self:
            rec.analytic_account_id.parent_id = rec.aa_id
        return res

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.analytic_account_id:
                rec.analytic_account_id.parent_id = False
        return super(Division_AA_lines, self).unlink()

    @api.multi
    def show_popup(self):
        ids = []
        ir_model_data = self.env['ir.model.data']
        division_tree_view = ir_model_data.get_object_reference('budget_management_AA', 'view_division_aa_dept_wizard')[1]
        if 'analytic_account_id' in self._context:
            parent_id = self._context.get('analytic_account_id')
            lines = self.search([
                ('analytic_account_id.parent_id.id','=',parent_id),
                ('from_date', '>=', self.from_date),
                ('to_date', '<=', self.to_date),
            ])
            ids = lines.ids

        return {
            'type': 'ir.actions.act_window',
            'view_type': 'tree',
            'view_mode': 'tree',
            'res_model': 'division.aa.lines',
            'views': [(division_tree_view, 'tree')],
            'view_id': division_tree_view,
            'target': 'new',
            'domain' : [('id','in',ids)]
        }

    @api.onchange('sub_dept_ids')
    def onchange_sub_dept_ids(self):
        total = 0.0
        for line in self.sub_dept_ids:
            total += line.amount
        if self._context.get('active_id'):
            self_obj = self.search([('id', '=', self._context.get('active_id'))])
            if self_obj.planned_amount < total:
                raise UserError('Warning.! \n Total Amount can not more than Planned Amount.')

class AccountAnalyticDistributionLine(models.Model):
    _inherit = 'account.analytic.distribution.line'

    @api.onchange('analytic_account_id')
    def onchange_analytic_account_id(self):
        if self.analytic_account_id:
            res = {}
            if not self.analytic_account_id.allow_over_limit and self.analytic_account_id.use_budget:
                res['warning'] = {'title': _('Warning'), 'message': _(
                    'Can not assigned this analytic account.')}
                self.analytic_account_id = False
            return res



class CrossoveredBudgetLinesInherit(models.Model):
    _inherit = "crossovered.budget.lines"

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
                                    (date_from, date_to, acc_ids,))
                result = self.env.cr.fetchone()[0] or 0.0
            line.practical_amount = result
            for child in line.analytic_account_id.child_ids:
                line.practical_amount += child.practical_amount

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    @api.model
    def compute_default_journal_id(self):
        journal_id = False
        context = self.env.context
        invoice = context.get('invoice', False)
        if invoice and invoice.id:
            origin = invoice.origin
            sale = self.env['sale.order'].search([
                ('name', '=', origin)
            ], limit=1)
            if sale and sale.id:
                journal_id = self.env.ref('stable_hr_timesheet_invoice.sale_journal')
        if not journal_id:
            active_model = context.get('active_model')
            if active_model == 'hr.expense' or context.get('search_default_submitted', False):
                journal_id = self.env.ref('stable_hr_timesheet_invoice.expense_journal')
        if not journal_id:
            ju = context.get('invoice')
            if ju:
                pu = self.env['account.invoice'].search([('id', '=', ju.id)], limit=1)
                if pu and pu.id:
                    if context.get('journal_type') == 'sale':
                        journal_id = self.env['account.journal'].search([('company_id','=',self.env.user.company_id.id),('name', '=', 'Customer Invoices')]).id
                    if context.get('journal_type') == 'purchase':
                        journal_id = self.env['account.journal'].search([('company_id','=',self.env.user.company_id.id),('name', '=', 'Vendor Bills')]).id
        if not journal_id:
            employee_obj = self.env['hr.employee']
            employees = employee_obj.search([('user_id', '=', context.get('user_id') or self.env.uid)])
            if employees:
                for employee in employees:
                    if employee.journal_id:
                        journal_id = employee.journal_id
                    else:
                        journal_id = self.env.ref('stable_hr_timesheet_invoice.timesheet_journal')
        return journal_id