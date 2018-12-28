# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import odoo.addons.decimal_precision as dp
import  base64

class HrExpense(models.Model):
    _inherit = "hr.expense"
    
    @api.depends('expense_line','expense_line.subtotal')
    def _compute_line_amount(self):
        for expense in self:
            total = 0.0
            for line in expense.expense_line:
                if line:
                    total += line.subtotal
            expense.total_amount = total

    boarding_pass = fields.Binary('Boarding Pass')
    boarding_pass_filename = fields.Char('Boarding Pass Filename')
    dtd_form = fields.Binary('DTD Form')
    dtd_form_filename = fields.Char('DTD Form Filename')
    meeting_agenda = fields.Binary('Meeting Agenda')
    meeting_agenda_filename = fields.Char('Meeting Agenda Filename')
    is_travel_expense = fields.Boolean('Travel Expense?', compute='_is_travel_expense')
    expense_line = fields.One2many("hr.expense.line","expense_id", string="Expense List")
    total_amount = fields.Float(string='Total Amount', store=True, compute='_compute_line_amount', digits=dp.get_precision('Account'))
    expense_submit_id = fields.Many2one('hr.expense', string='Expense To Submit')
    expense_report = fields.Binary(string='Expense To Submit')
    unit_amount = fields.Float(string='Unit Price', readonly=False)
    quantity = fields.Float( readonly=False, default=1)
    expense_sheet_id = fields.Many2one('hr.expense.sheet',string='Expense Sheet')

    @api.onchange('product_id')
    def _is_travel_expense(self):
        for hr in self:
            if hr.product_id and hr.product_id.name.lower().find('travel') == -1:
                hr.is_travel_expense = False
            else:
                hr.is_travel_expense = True

    @api.multi
    def submit_expenses(self):
        if self.expense_sheet_id:
            vals = {}
            vals['employee_id'] = self.employee_id.id
            vals['name'] = self.name if len(self.ids) == 1 else ''
            vals['responsible_id'] = self.employee_id.parent_id.user_id.id
            vals['boss_id'] = self.employee_id.boss_id.user_id.id
            vals['state'] = 'check'
            expense_sheet_id = self.env['hr.expense.sheet'].write(vals)
            for ex_sh in self.expense_sheet_id.expense_line_ids:
                ex_sh.state = 'draft'
                ex_sh.unlink()

            for expense in self:
                pdf = self.env['report'].sudo().get_pdf([self.expense_sheet_id.id], 'hr_expense.report_expense_sheet')
                if pdf:
                    linevals = {}
                    linevals['product_id'] = expense.product_id.id
                    linevals['date'] = fields.Datetime.now()
                    linevals['name'] =  self.expense_sheet_id.name
                    linevals['expense_report'] = base64.encodestring(pdf)
                    linevals['unit_amount'] = 10.00
                    linevals['sheet_id'] = self.expense_sheet_id.id
                    linevals['expense_line'] = [(6,0,expense.expense_line.ids)]
                    linevals['total_amount'] = expense.total_amount
                    self.expense_sheet_id.expense_line_ids = [(0, 0, linevals)]

            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'hr.expense.sheet',
                'res_id': self.expense_sheet_id.id,
                'target': 'current',
            }
        else:
            if any(expense.state != 'draft' for expense in self):
                raise UserError(_("You cannot report twice the same line!"))
            if len(self.mapped('employee_id')) != 1:
                raise UserError(_("You cannot report expenses for different employees in the same report!"))

            vals = {}
            vals['employee_id'] = self.employee_id.id
            vals['name'] = self.name if len(self.ids) == 1 else ''
            vals['responsible_id'] = self.employee_id.parent_id.user_id.id
            vals['boss_id'] = self.employee_id.boss_id.user_id.id
            vals['state'] = 'check'
            expense_sheet_id = self.env['hr.expense.sheet'].create(vals)

            for expense in self:
                expense.expense_sheet_id = expense_sheet_id.id
                pdf = self.env['report'].sudo().get_pdf([expense_sheet_id.id], 'hr_expense.report_expense_sheet')
                if pdf:
                    linevals = {}
                    linevals['product_id'] = expense.product_id.id
                    linevals['date'] = fields.Datetime.now()
                    linevals['name'] =  expense_sheet_id.name
                    linevals['expense_report'] = base64.encodestring(pdf)
                    linevals['unit_amount'] = 10.00
                    linevals['sheet_id'] = expense_sheet_id.id
                    linevals['expense_line'] = [(6,0,expense.expense_line.ids)]
                    linevals['total_amount'] = expense.total_amount
                    expense_sheet_id.expense_line_ids = [(0, 0, linevals)]
            return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'hr.expense.sheet',
                'res_id': expense_sheet_id.id,
                'target': 'current',
            }

    # @api.multi
    # def submit_expenses(self):
    #     if any(expense.state != 'draft' for expense in self):
    #         raise UserError(_("You cannot report twice the same line!"))
    #     if len(self.mapped('employee_id')) != 1:
    #         raise UserError(_("You cannot report expenses for different employees in the same report!"))
    #     return {
    #         'type': 'ir.actions.act_window',
    #         'view_mode': 'form',
    #         'res_model': 'hr.expense.sheet',
    #         'target': 'current',
    #         'context': {
    #             'default_expense_line_ids': [line.id for line in self],
    #             'default_employee_id': self[0].employee_id.id,
    #             'default_name': self[0].name if len(self.ids) == 1 else '',
    #             'default_responsible_id': self[0].employee_id.parent_id.user_id.id,
    #             'default_boss_id': self[0].employee_id.boss_id.user_id.id,
    #             # 'default_state': self[0].is_travel_expense and 'check' or 'review'
    #         }
    #     }

class HrExpenseLine(models.Model):
    _name = "hr.expense.line"
    
    @api.one
    @api.depends('amount','rate')
    def _compute_subtotal(self):
        for rec in self:
            rec.subtotal = rec.amount * rec.rate
        
    expense_id = fields.Many2one("hr.expense","Expense")
    itemize_expense_id = fields.Many2one("itemize.expense", string="Itemize Expense")
    amount = fields.Float("Amount")
    bill_reference = fields.Char("Bill Reference")
    account_id = fields.Many2one("account.account", string="Account", default=lambda self: self.env['ir.property'].get('property_account_expense_categ_id', 'product.category'))
    currency_id = fields.Many2one("res.currency", string="Currency")
    rate = fields.Float("Rate")
    subtotal = fields.Float("Subtotal In Payment Currency", compute='_compute_subtotal')
    
    @api.onchange('itemize_expense_id')
    def onchange_itemize_expense(self):
        if self.itemize_expense_id:
            self.account_id = self.itemize_expense_id.account_id
    
class HrExpenseLine(models.Model):
    _name = "itemize.expense"
    
    name = fields.Char("Itemize Expense")
    account_id = fields.Many2one("account.account", string="Account", required=True, default=lambda self: self.env['ir.property'].get('property_account_expense_categ_id', 'product.category'))
    

class HrExpenseSheet(models.Model):
    _inherit = "hr.expense.sheet"

    state = fields.Selection([('check', 'Checking'),
                              ('submit', 'Submitted'),
                              ('approve', 'Approved'),
                              ('post', 'Posted'),
                              ('done', 'Paid'),
                              ('cancel', 'Refused')
                              ], default='check')
    boss_id = fields.Many2one('res.users', 'Final Validation By', readonly=True, copy=False)

    # @api.multi
    # def review_expense_sheets(self):
    #     template = self.env.ref('modifier_teo_hr.expense_review_template')
    #     sent_mail = template.send_mail(self.id, force_send=True, raise_exception=False)
    #     if sent_mail:
    #         self.write({'state': 'check'})

    @api.multi
    def check_expense_sheets(self):
        if not self.user_has_groups('account.group_account_user'):
            raise UserError(_("Only Accountant can Checking expenses"))
        template = self.env.ref('modifier_teo_hr.expense_check_template')
        sent_mail = template.send_mail(self.id, force_send=True, raise_exception=False)
        if sent_mail:
            self.write({'state': 'submit'})
        
    @api.multi
    def approve_expense_sheets(self):
        expense_id = self.env['hr.expense'].browse(self._context.get('active_id'))
        employee_id = self.env['hr.employee'].search([('name','ilike','albert')], limit=1)
        if expense_id.is_travel_expense:
            if self.env.user == self.boss_id:
                template = self.env.ref('modifier_teo_hr.expense_approved_template')
                sent_mail = template.send_mail(self.id, force_send=True, raise_exception=False)
                if sent_mail:
                    self.write({'state': 'approve', 'responsible_id': self.env.user.id})
            else:
                raise UserError(_("Only Boss can Approve Travel Expense."))
        else:
            if employee_id and employee_id[0].user_id and employee_id[0].user_id == self.env.user:
                template = self.env.ref('modifier_teo_hr.expense_approved_template')
                sent_mail = template.send_mail(self.id, force_send=True, raise_exception=False)
                if sent_mail:
                    self.write({'state': 'approve', 'responsible_id': self.env.user.id})
            else:
                raise UserError(_("Only Albert can Approve Other Expense."))