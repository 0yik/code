# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#    Copyright (C) 2011-Today Serpent Consulting Services Pvt. Ltd. (<http://serpentcs.com>).
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
from odoo import api, models
import time


class company_total_payroll_report_tmp(models.AbstractModel):
    _name = 'report.teo_payroll.company_total_payroll_report_tmp'

    @api.model
    def get_name(self, data):
        date_from = data.get('date_from' or False)
        date_to = data.get('date_to' or False)
        payslip_result = []
        count=0
        employee_ids = self.env['hr.employee'].search([])
        for employee in employee_ids:
            payslip_ids = self.env['hr.payslip'].search([('employee_id', '=', employee.id),
                                                         ('date_from', '>=', date_from),
                                                         ('date_from', '<=', date_to), 
                                                         ('state', 'in', ['draft', 'done', 'verify'])])
            twage = overtime = net = twage = gross = cpf = pf = alw = ded = 0.0
            for payslip in payslip_ids:
                count = count+1
                twage =  payslip.contract_id.wage_to_pay
                for rule in payslip.details_by_salary_rule_category:
                    if rule.code == 'SC102':
                        overtime += rule.total
                    if rule.code == 'NET':
                        net += rule.total
                    if rule.code == 'GROSS':
                        gross += rule.total
                    if rule.category_id.code == 'CAT_CPF_EMPLOYEE':
                        cpf += rule.total
                    if rule.category_id.code == 'CAT_CPF_EMPLOYER':
                        pf += rule.total
                    if rule.category_id.code == 'ALW':
                        alw += rule.total
                    if rule.category_id.code == 'DED':
                        ded += rule.total

                    
            payslip_result.append({
                              'twage': twage or 0.0,
                              'ot':overtime or 0.0,
                              'net': net or 0.0,
                              'gross': gross or 0.0,
                              'pf': pf or 0.0,
                              'cpf': cpf or 0.0,
                              'alw':alw or 0.0,
                              'ded':ded or 0.0,
                              })
        return payslip_result,count
    
    @api.multi
    def render_html(self, docids, data):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_id'))
        data = docs.read([])[0]
        get_name,count = self.get_name(data)
        docargs = {'doc_ids' : self.ids,
                   'doc_model' : self.model,
                   'data' : data,
                   'docs' : docs,
                   'time' : time,
                   'get_name' : get_name,
                   'count_line':count,
                   
                   }
        return self.env['report'].render('teo_payroll.company_total_payroll_report_tmp', docargs)
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
