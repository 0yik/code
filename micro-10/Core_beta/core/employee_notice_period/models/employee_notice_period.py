# -*- coding: utf-8 -*-


from openerp import api, exceptions, fields, models, _


class EmployeeNoticePeriod(models.Model):
    _name = 'employee.notice.period'
    _description = 'Employee Notice Period'
    _rec_name = 'duration'

    duration = fields.Integer(
        string='Notice Period', help='Add days of notice period.')
    employee_ids = fields.Many2many(
        comodel_name='hr.employee', string='Employees',
        help='Add employee here.')

    @api.multi
    def action_assign(self):
        """docstring for action_assign"""
        for obj in self:
            if not obj.employee_ids:
                raise exceptions.UserError(_("Please add employee first."))
            obj.employee_ids.write({'notice_period_id': obj.id})
        return True


EmployeeNoticePeriod()
