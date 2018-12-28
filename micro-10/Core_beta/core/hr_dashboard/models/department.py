# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2017 Serpent Consulting Services Pvt. Ltd.
#    Copyright (C) 2017 OpenERP SA (<http://www.serpentcs.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    a_age = fields.Integer(compute="_employee_age_cal",
                           string="Average Age")
    total_age = fields.Integer(compute="_employee_age_cal",
                               string="Total Age")
    num_emp = fields.Integer(compute="_employee_age_cal",
                             string="Total Number Of Employee")

    @api.multi
    def _employee_age_cal(self):
        emp_obj = self.env['hr.employee']
        for dep in self:
            employees = emp_obj.search([('department_id', '=', dep.id)])
            dep.a_age, dep.total_age, dep.num_emp = emp_obj.calculation(employees)
