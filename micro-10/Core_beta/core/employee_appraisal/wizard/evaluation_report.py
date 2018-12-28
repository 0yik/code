# -*- coding: utf-8 -*-
from odoo import fields,models,api
from odoo.tools.translate import _
from odoo.exceptions import UserError, RedirectWarning, ValidationError

class evaluation_report(models.Model):
    _name="evaluation.report"
    _rec_name = "emp_name"


    report_type=fields.Selection([ ('emp_based','Employee Based'),
                                   ('dep_based','Department Based'),
                                 ],string="Report Type")
    emp_name=fields.Many2one('hr.employee',string="Employee Name")
    emp_id=fields.Char(string="Emp Id")
    year=fields.Many2one('hr.year',string="Year")
    quarter=fields.Selection([  ('q1','Q1'),
                                ('q2','Q2'),
                                ('q3','Q3'),
                                ('q4','Q4'),
                             ],string="Quarter")
    joining_date=fields.Date(string="Joining Date")
    department_id=fields.Many2one('hr.department',string="Department")
    emp_image=fields.Binary(string="Photo")
    eval_report_rating_ids=fields.One2many('emp.rating.lines','eval_report_rating_id',string="")

    @api.onchange('emp_name','year','quarter')
    def onchange_year(self):
        ''' On change over the fields Employee, year, quarter and return the Lines. 
            If no records raises the warning.
        '''
        if self.emp_name and self.year and self.quarter:
            obj = self.env['employee.evaluation'].search([('emp_id','=',self.emp_name.id),('employee_id','=',self.emp_name.emp_id),('year','=',self.year.id),('quarter','=',self.quarter)],limit=1) or False
            if obj:
                    self.emp_id = self.emp_name.emp_id
                    self.joining_date = self.emp_name.join_date
                    self.department_id = self.emp_name.department_id.id
    
                    self.eval_report_rating_ids = [(0,0,{'quarter':obj.quarter,'rating_label_id':line.rating_label_id.id,'rating':line.rating,'comment':line.comment }) for line in obj.emp_rating_ids]
        
            else:
                    self.eval_report_rating_ids = False
                    return {'warning':{'message':'Sorry, records not found'}}



    @api.multi
    def eval_report(self):
        ''' Method Called from 'Submit' button action in the wizard of Evaluation Report.
	    Will Print the report based on the Type selected.
	 '''
        # Report type: Employee based
        if self.report_type == 'emp_based':
            lst=[]
            obj = self.env['employee.evaluation'].search([('emp_id','=',self.emp_name.id),('employee_id','=',self.emp_name.emp_id),('year','=',self.year.id),('quarter','=',self.quarter)],limit=1) or False
            if obj:
                obj.write({'is_year':False})
            else:
                 raise ValidationError(_('Sorry,Records not found'))       
            lst.append(obj.id)
            datas = {
                    'ids':lst,
                    'model':'employee.evaluation',
                    }
        # Report type: Department based
        elif self.report_type == 'dep_based':
                dep_objs = self.env['hr.employee'].search([('department_id','=',self.department_id.id)])
                lst = []
                for dep_obj in dep_objs:
                    obj = self.env['employee.evaluation'].search([('emp_id','=',dep_obj.id),('employee_id','=',dep_obj.emp_id),('year','=',self.year.id),('quarter','=',self.quarter)],limit=1)
                    if obj.id:
                        obj.write({'is_year':False})
                        lst.append(obj.id)
                if not lst:
                    raise ValidationError(_('Sorry,Records not found'))

                datas = {
                             'ids':lst,
                             'model':'employee.evaluation',
                        }
        return {
                'type':'ir.actions.report.xml',
                'report_name':'employee_appraisal.report_employee_evaluation',
                'datas':datas,
                }

