# -*- coding: utf-8 -*-


from openerp import api, exceptions, fields, models, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    notice_period_id = fields.Many2one(
        comodel_name='employee.notice.period', string='Notice Period', help='')


HrEmployee()
