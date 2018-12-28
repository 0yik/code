# -*- coding: utf-8 -*-

##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2017-TODAY Cybrosys Technologies(<http://www.cybrosys.com>).
#    Author: Nikhil krishnan(<http://www.cybrosys.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import fields, models, tools, api


class PayrollReportView(models.Model):
    _inherit = 'hr.payroll.report.view'

    rule_name = fields.Char('Salary Rule')
    rule_category_name = fields.Char('Salary Rule Category')
    net = fields.Float(string='Salary')

    def _select(self):
        select_str = """
        min(ps.id) as id,emp.id as name,jb.id as job_id,
        dp.id as department_id,cmp.id as company_id, 
        ps.date_from,hsr.name as rule_name, hsrc.name as rule_category_name, ps.date_to, psl.total as net, ps.state as state
        
        """
        return select_str

    def _from(self):
        from_str = """
            hr_payslip_line psl  join hr_payslip ps on (ps.employee_id=psl.employee_id and ps.id=psl.slip_id)
            join hr_employee emp on (ps.employee_id=emp.id) join hr_department dp on (emp.department_id=dp.id) 
            JOIN hr_salary_rule hsr ON psl.salary_rule_id = hsr.id 
            JOIN hr_salary_rule_category hsrc ON psl.category_id = hsrc.id 
            join hr_job jb on (emp.department_id=jb.id) join res_company cmp on (cmp.id=ps.company_id)
         """
        return from_str

    def _group_by(self):
        group_by_str = """
            group by emp.id,psl.total,hsr.name,hsrc.name,ps.date_from, ps.date_to, ps.state,jb.id,dp.id,cmp.id
        """
        return group_by_str

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as ( SELECT
               %s
               FROM %s
               %s
               )""" % (self._table, self._select(), self._from(), self._group_by()))


# _________________Query________________________

# select emp.name_related as name,emp.id as employee_id,jb.name as job,jb.id as job_id,
#         dp.name as department,dp.id as department_id,cmp.name as company,cmp.id as company_id,
#         ps.date_from, ps.date_to, sum(psl.total) as net, ps.state as state from hr_payslip_line psl  join hr_payslip
#         ps on (ps.employee_id=psl.employee_id and ps.id=psl.slip_id)
#             join hr_employee emp on (ps.employee_id=emp.id) join hr_department dp on (emp.department_id=dp.id)
#             join hr_job jb on (emp.department_id=jb.id) join res_company cmp on (cmp.id=ps.company_id) where
#         psl.code='NET'  group by emp.name_related,emp.id,psl.total,ps.date_from, ps.date_to, ps.state,dp.name,jb.name,
#         cmp.name,jb.id,dp.id,cmp.id
