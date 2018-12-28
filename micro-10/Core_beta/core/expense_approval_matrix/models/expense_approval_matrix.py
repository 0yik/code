# -*- coding: utf-8 -*-
from odoo import fields, models


class expense_approval_matrix(models.Model):
    _name = 'expense.approval.matrix'
    _rec_name = 'product_doa'
    _inherit = ['mail.thread']
    _description = 'Expense Approval Matrix'

    product_doa = fields.Char('Name', track_visibility='onchange')
    # department_id = fields.Many2one(
    # 'hr.department', string='Department', track_visibility='onchange')
    department_ids = fields.Many2many(
        'hr.department', string='Department', track_visibility='onchange')
    approval_line_ids = fields.One2many(
        'expense.approval.matrix.lines', 'approval_line_id', 'Lines')
    approval_method = fields.Selection(
        selection=[
            ('more_approval', 'The more the expense amount submitted, the more level of approval included'),
            ('direct_approval', 'Expense amount submitted will be compared directly with the set range of amount')
        ], required=True, default='more_approval',
        string='Approval Method', help='Select approval method.')


expense_approval_matrix()


class expense_approval_matrix_lines(models.Model):
    _name = 'expense.approval.matrix.lines'
    _description = "Expense Approval Matrix Line"
    _order = 'sequence_no asc'

    approval_line_id = fields.Many2one('expense.approval.matrix', 'Approval')
    sequence_no = fields.Integer('Sequence')
    # employee_id = fields.Many2one('hr.employee', 'Employee')
    employee_ids = fields.Many2many('hr.employee', string='Employees')
    min_amount = fields.Float('Minimum Amount')
    max_amount = fields.Float('Maximum Amount')


expense_approval_matrix_lines()
