# -*- coding: utf-8 -*-

import odoo.addons.decimal_precision as dp
import time
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, float_compare
from odoo.exceptions import Warning

class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    def get_salary_rule_result(self, employee, payslip, code):
        res = 0.0
        if employee.bpjs_ketenagakerjaan_number:
            if code == 'JKKER':
                if payslip.contract_id.wage < (employee.province_id and employee.province_id.min_wage or 0):
                    res = (employee.province_id.min_wage * employee.jkk_percentage) / 100
                else:
                    res = (payslip.contract_id.wage * employee.jkk_percentage) / 100
            if code == 'JKMER':
                if payslip.contract_id.wage < (employee.province_id and employee.province_id.min_wage or 0):
                    res = (employee.province_id.min_wage * 0.3) / 100
                else:
                    res = (payslip.contract_id.wage * 0.3 ) / 100
            if code == 'JPEE1':
                if payslip.contract_id.wage < (employee.province_id and employee.province_id.min_wage or 0):
                    res = (employee.province_id.min_wage) / 100
                elif payslip.contract_id.wage > employee.user_id.company_id.bpjs_ketenagakerjaan_max:
                    res = (employee.user_id.company_id.bpjs_ketenagakerjaan_max) / 100
                else:
                    res = (payslip.contract_id.wage) / 100
            if code == 'JHTEE2':
                if payslip.contract_id.wage < (employee.province_id and employee.province_id.min_wage or 0):
                    res = (employee.province_id.min_wage * 2) / 100
                else:
                    res = (payslip.contract_id.wage * 2) / 100
            if code == 'JHTER':
                if payslip.contract_id.wage < (employee.province_id and employee.province_id.min_wage or 0):
                    res = (employee.province_id.min_wage * 3.7) / 100 
                else:
                    res = (payslip.contract_id.wage * 3.7) / 100
            if code == 'JPER':
                if payslip.contract_id.wage < (employee.province_id and employee.province_id.min_wage or 0):
                    res = (employee.province_id.min_wage * 2) / 100
                elif payslip.contract_id.wage > employee.user_id.company_id.bpjs_ketenagakerjaan_max:
                    res = (employee.user_id.company_id.bpjs_ketenagakerjaan_max * 2) / 100
                else:
                    res = (payslip.contract_id.wage * 2) / 100
            if code == 'BPJSKES4':
                if payslip.contract_id.wage < (employee.province_id and employee.province_id.min_wage or 0):
                    res = (employee.province_id.min_wage * 4) / 100
                elif payslip.contract_id.wage > employee.user_id.company_id.bpjs_kesehatan_max:
                    res = (employee.user_id.company_id.bpjs_kesehatan_max * 4) / 100
                else:
                    res = (payslip.contract_id.wage * 4) / 100
            if code == 'BPJSKES1':
                if payslip.contract_id.wage < (employee.province_id and employee.province_id.min_wage or 0):
                    res = (employee.province_id.min_wage) / 100
                elif payslip.contract_id.wage > employee.user_id.company_id.bpjs_kesehatan_max:
                    res = (employee.user_id.company_id.bpjs_kesehatan_max) / 100
                else:
                    res = (payslip.contract_id.wage) / 100
        return res