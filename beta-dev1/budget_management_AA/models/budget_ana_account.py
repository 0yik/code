from odoo import api, fields, models
from datetime import datetime
from odoo.exceptions import UserError


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    budget_setting = fields.Boolean('Disallow Over limit budget (Show Warning if passed Planned Amount.)',
        help='Disallow Over limit budget (Show Warning if passed Planned Amount.)')

    @api.one
    def _set_budget_setting(self):
        config_id = self.env['ir.config_parameter'].search([('key', '=', 'Budget.Setting')])
        if config_id:
            config_id.value = str(self.budget_setting)

    @api.one
    def _get_budget_setting(self):
        config_id = self.env['ir.config_parameter'].search([('key', '=', 'Budget.Setting')])
        if config_id:
            value = False
            if config_id.value == 'False':
                value = False
            else:
                value = True
            self.budget_setting = value

class BudgetAnalyticAccount(models.Model):
    _name = 'budget.analytic.account'
    _inherit = 'mail.thread'
    _description = 'Budget Analytic Account'
    _rec_name = 'budget_id'

    budget_id = fields.Many2one('crossovered.budget', 'Budget Financial No.')
    from_date = fields.Date(default=datetime.now().date())
    to_date = fields.Date()
    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting_for_approval', 'Waiting for Approval'),
        ('validated', 'Validated'),
    ], 'Status', default='draft', index=True, track_visibility='always')
    crossovered_budget_items = fields.One2many('budget.aa.lines', 'budget_aa_id', string="Budget AA")

    @api.multi
    def submit_for_approval(self):
        self.write({'state': 'waiting_for_approval'})

    @api.multi
    def button_approve(self):
        self.write({'state': 'validated'})

    @api.multi
    def button_set_to_draft(self):
        self.write({'state': 'draft'})

    @api.onchange('budget_id')
    def onchange_budget_id(self):
        if self.budget_id:
            self._context
            self.from_date = self.budget_id.date_from
            self.to_date = self.budget_id.date_to
            list = []
            for line in self.budget_id.crossovered_budget_line:
                list.append({
                            'general_budget_id': line.general_budget_id.id,
                            'analytic_account_id': line.analytic_account_id.id,
                            'from_date': line.date_from,
                            'to_date': line.date_to,
                            'planned_amount': line.planned_amount
                            })
            self.crossovered_budget_items = list

class Budget_AA_lines(models.Model):
    _name = 'budget.aa.lines'

    budget_aa_id = fields.Many2one('budget.analytic.account')
    general_budget_id = fields.Many2one('account.budget.post', 'Budgetary Position')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account')
    from_date = fields.Date(default=datetime.now().date(), string="Start Date")
    to_date = fields.Date(string="End Date")
    planned_amount = fields.Float("Planned Amount")
    reserved_amount = fields.Float("Reserved Amount")
    allocation_amount = fields.Float("Allocation Amount")
    practical_amount = fields.Float("Practical Amount")
    theoritical_amount = fields.Float("Theoritical Amount")
    achievement = fields.Float("Achievement")
    sub_dept_ids = fields.One2many('sub.dept.descendant.line', 'budget_aa_line_id', string='Sub-Dept')

    @api.multi
    def show_popup(self):
        ir_model_data = self.env['ir.model.data']
        sub_dept_form_id = ir_model_data.get_object_reference('budget_management_AA', 'view_sub_dept_wizard')[1]

        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'budget.aa.lines',
            'res_id': self.id,
            'views': [(sub_dept_form_id, 'form')],
            'view_id': sub_dept_form_id,
            'target': 'new',
            'context': {'active_id': self.id}
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

class SubDeptDescendantLine(models.Model):
    _name = 'sub.dept.descendant.line'

    name = fields.Char(string="Sub-Dept/Descendant")
    amount = fields.Float(string="Amount")
    budget_aa_line_id = fields.Many2one('budget.aa.lines')
