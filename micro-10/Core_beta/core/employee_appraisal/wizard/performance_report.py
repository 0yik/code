#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from odoo import fields,models,api
from odoo.tools.translate import _
from odoo.exceptions import UserError, RedirectWarning, ValidationError

class performance_report(models.Model):
    _name="performance.report"
    _rec_name = "emp_name"
    _description = 'Performance Report'
    
    emp_name=fields.Many2one('hr.employee',string="Employee Name")
    year=fields.Many2one('hr.year',string="Year")
    emp_id = fields.Char(string="Employee Id")
    joining_date=fields.Date(string="Joining Date")
    department_id=fields.Many2one('hr.department',string="Department")
    perf_report_rating_ids=fields.One2many('emp.rating.lines','perf_report_rating_id',string="")
    report_type=fields.Selection([ ('emp_based','Employee Based'),
                                   ('dep_based','Department Based'),
                                 ],string="Report Type")
    @api.onchange('emp_name','year')
    def onchange_year(self):
        ''' On change over the fields Employee name, Year to populate the remaining fields. '''
        if self.emp_name and self.year:
            self.emp_id = self.emp_name.emp_id
            self.joining_date=self.emp_name.join_date
            self.department_id=self.emp_name.department_id.id
            
            eval_obj = self.env['employee.evaluation'].search([('emp_id','=',self.emp_name.id),('year','=',self.year.id)]) or False
            if eval_obj:
                    lst = []
                    for obj in eval_obj:
                        for line in obj.emp_rating_ids:
                            lst.append( (0,0,{'quarter':obj.quarter,'rating_label_id':line.rating_label_id.id,'rating':line.rating.id,'comment':line.comment}) )
                    self.perf_report_rating_ids=lst
            else:
                    self.perf_report_rating_ids = False
                    return {'warning':{'message':'Sorry, records not found'}}

    

    @api.multi
    def emp_perf_report(self):
        ''' Method called from 'Print' button action in the Performance Report wizard.
	    Will Print based on the type selected.
	'''
        #Report Type: Employee
        if self.report_type == 'emp_based':
            eval_obj = self.env['employee.evaluation'].search([('emp_id','=',self.emp_name.id),('year','=',self.year.id)],limit=1) or False
            if not eval_obj:
                raise ValidationError(_('Sorry,Records not found'))
            eval_obj.write( {'is_year':True} )
            data = {
                     'ids':[eval_obj.id],
                     'model':'employee.evaluation',
                   }
        #Report Type: Deaprtment
        elif self.report_type == 'dep_based':
                dep_objs = self.env['hr.employee'].search([('department_id','=',self.department_id.id)])
                lst = []
                for dep_obj in dep_objs:
                    obj = self.env['employee.evaluation'].search([('emp_id','=',dep_obj.id),('year','=',self.year.id)],limit=1) or False
                    if obj:
                        obj.write({'is_year':True})
                        lst.append(obj.id)
                if not lst:
                    raise ValidationError(_('Sorry,Records not found'))
                data = {
                             'ids':lst,
                             'model':'employee.evaluation',
                        }
        return {
                    'type': 'ir.actions.report.xml',
                    'report_name':'employee_appraisal.report_employee_evaluation',
                    'datas':data
                   }
    
class employee_performance(models.Model):
    _name = "employee.performance"
    _description = 'Employee Performance'
    
    emp_name=fields.Many2one('hr.employee',string="Employee Name")
    year=fields.Many2one('hr.year',string="Year")
    department_id=fields.Many2one('hr.department',string="Department")
    emp_perf_rating_ids=fields.One2many('emp.rating.lines','emp_perf_rating_id',string="")
