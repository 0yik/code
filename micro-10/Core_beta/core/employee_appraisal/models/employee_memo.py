# -*- coding: utf-8 -*- 
from odoo import fields,models,api
from datetime import date, datetime

class employee_memo(models.Model):

    _name = 'employee.memo'

    name=fields.Char(string="Sequence No")
    emp_name = fields.Many2one('hr.employee',string="Employee")
    emp_id = fields.Char(string="Employee ID")
    date = fields.Date(string="Date", default=date.today().strftime("%Y-%m-%d"))
    memo_desc=fields.Text(string="Memo Description")
    quarter=fields.Selection([  ('q1','Q1'),
                                ('q2','Q2'),
                                ('q3','Q3'),
                                ('q4','Q4'),
                                ],string="Quarter")
    year=fields.Many2one('hr.year',string="Year")
    memo_type=fields.Selection([ ('positive','Positive'),
                            ('negative','Negative'),
                          ],string="Type")
    memo_history_id = fields.Many2one('emp.memo.history',string=" ")                          


    @api.model
    def create(self, vals):
        ''' Method overriden to
	    1) To Generate sequence Id
	    2) write the memo in the Employee Memo history
	'''
	### To Generate the Sequence Code.
        vals['name'] = self.env['ir.sequence'].next_by_code('employee.memo') or '/'
        return super(employee_memo, self).create(vals)


    @api.onchange('emp_name')
    def onchange_empname(self):
	''' On change over the field 'Employee' to populate the EMP ID on the form.'''
        if self.emp_name:
             self.emp_id = self.emp_name.emp_id
        else:
             self.emp_id = False
    
