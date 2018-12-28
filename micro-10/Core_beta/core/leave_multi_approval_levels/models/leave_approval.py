# -*- coding: utf-8 -*-


from openerp import api, exceptions, fields, models, _


class LeaveApproval(models.Model):
    _name = 'leave.approval'
    _description = 'Leave Approval'

    name = fields.Char(string='Name', size=64, help='Name', required=True, )
   # department_id = fields.Many2one(
   #    comodel_name='hr.department', string='Department', help='Department')
    department_ids = fields.Many2many(
        comodel_name='hr.department', string='Departments', help='')
   # leave_type_id = fields.Many2one(
   #    comodel_name='hr.holidays.status',
   #    string='Leave Type', help='Leave type')
    leave_type_ids = fields.Many2many(
        comodel_name='hr.holidays.status', string='Leave Type',
        help='Add multiple leave type.')
    approval_line_ids = fields.One2many(
        comodel_name='leave.approval.line',
        inverse_name='leave_approval_id', string='Leave Approval', help='')


LeaveApproval()


class LeaveApprovalLine(models.Model):
    _name = 'leave.approval.line'
    _description = 'Leeve Approval Line'
    _order = 'sequence asc'

    sequence = fields.Integer(string='Sequence', help='Sequence', default=1, )
    employee_ids = fields.Many2many(
        comodel_name='hr.employee',
        string='Employee', help='Add multiple employee as approver.')
    leave_approval_id = fields.Many2one(
        comodel_name='leave.approval', string='Leave Approval', help='')


LeaveApprovalLine()
