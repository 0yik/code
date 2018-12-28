# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-Today Serpent Consulting Services Pvt. Ltd.
#    (<http://serpentcs.com>).
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
from odoo import fields, api, models
from odoo.exceptions import ValidationError


class hr_contract(models.Model):

    _inherit = 'hr.contract'

    wage_to_pay = fields.Float('Wage To Pay',help='This Wage to pay value is display on payroll report')
    rate_per_hour = fields.Float('Rate per hour')
    active_employee = fields.Boolean(related='employee_id.active', string="Active Employee")

#    @api.constrains('date_end','date_start')
#    def _check_date(self):
#        for contract in self:
#            domain = [('date_start', '<=', contract.date_end),
#                      ('date_end', '>=', contract.date_start),
#                      ('employee_id', '=', contract.employee_id.id),
#                      ('id', '!=', contract.id)]
#            contract_ids=self.search(domain, count=True)
#            if contract_ids:
#                raise ValidationError('You can not have 2 contract that overlaps on same date!')
#        return True

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.job_id = self.employee_id.job_id
            self.department_id = self.employee_id.department_id
            self.active_employee = self.employee_id.active

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
