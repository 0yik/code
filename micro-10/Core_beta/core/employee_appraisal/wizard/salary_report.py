#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from odoo import api,models,fields
from odoo.exceptions import UserError,ValidationError
from datetime import date

class salary_report(models.Model):
    _name='salary.report'
    _description = 'Salary Report'
    
    name = fields.Many2one('hr.employee',string="Employee Name")
    year = fields.Many2one('hr.year',string="Year")
    employee_id = fields.Char(string="Employee ID")
    curr_salary=fields.Float(string="Current Salary")
    date=fields.Date(string="Date")
    calculated_increment = fields.Float(string="Calculated Increment")
    management_round_off = fields.Float(string="Management Round Off")
    final_increment = fields.Float(string="Final Increment")
    increment_per=fields.Float(string="Increment %")
    management_comments = fields.Text(string="Management Comments")


    @api.onchange('name','year')
    def onchange_emp_name(self):
        ''' On change over the fields Employee and Year to populate the remaining all the fileds in the wizard.'''
        if self.name and self.year :	    
            salary_id = self.env['employee.evaluation'].search([('emp_id','=',self.name.id),('employee_id','=',self.name.emp_id),('year','=',self.year.id),('quarter','=','q4')],limit=1)
            if salary_id :
                tot = 0.0
                req_tot = 0.0
                self.employee_id = salary_id.emp_id.emp_id
                self.curr_salary = salary_id.current_salary
                self.date = date.today()
                self.calculated_increment = salary_id.calculated_increment
                self.management_round_off = salary_id.mngmt_roundoff
                self.final_increment = salary_id.final_increment
                tot = salary_id.final_increment-salary_id.current_salary
                if salary_id.current_salary > 0:
                    fin_sal = salary_id.final_salary
                    req_tot = float(((fin_sal-salary_id.current_salary)/salary_id.current_salary)*100)
                self.increment_per = req_tot
                self.management_comments = salary_id.mngmt_comments
            else:
                self.name,self.year = False, False     
                return {'warning':{'message':('There are no records for selected Employee and Year')}}
    
    @api.multi
    def print_report(self):
        ''' Method called from 'Print' button action in the Wizard of Salary Report.'''
        if self.name and self.year :
    	    datas = {
    	 		'ids' : [self.id],
    	 		'model' : 'salary.report',
    	    }

            return {
        	'type': 'ir.actions.report.xml',
        	'report_name' : 'employee_appraisal.report_employee_salary_id',
        	'datas' : datas
            }
	
