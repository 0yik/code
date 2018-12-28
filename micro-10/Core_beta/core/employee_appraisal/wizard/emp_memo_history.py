# -*- coding: utf-8 -*- 

from odoo import api,fields,models
from odoo.exceptions import ValidationError,UserError

class emp_memo_history(models.Model):
    _name = 'emp.memo.history'
    _rec_name = 'emp_name'
    _description = 'Employee Memo History(Report)'
    
    
    emp_name = fields.Many2one('hr.employee',string="Employee")
    emp_id=fields.Char(string="Employee ID")
    job_title=fields.Many2one('hr.job',string="Job Title")
    join_date=fields.Date(string="Joining Date")
    department_id=fields.Many2one('hr.department',string="Department")
    supervisor_name=fields.Many2one('hr.employee',string="Supervisor Name")
    emp_status=fields.Selection([ ('casual','Casual'),
                                  ('new_hire','New Hire'),
                                  ('permanent','Permanent'),
                                  ('terminated','Terminated'),
                                ],string="Employment Status")
    emp_memo_history_ids = fields.One2many('employee.memo','memo_history_id',string='')
  
    report_type = fields.Selection([('employee','Employee'),('department','Department')],string='Report Type')
    is_memo_button = fields.Boolean(string="Is Button",default=False)

    @api.onchange('emp_name')
    def onchange_emp_name(self):
        ''' Onchange over the Field Employee to populate the EMP ID, Job, Join date, Depart, Supervisor and Lines. '''
    	if self.emp_name:
    	    self.emp_id = self.emp_name.emp_id
    	    self.job_title = self.emp_name.job_id.id
    	    self.join_date = self.emp_name.join_date
    	    self.department_id = self.emp_name.department_id.id
    	    self.supervisor_name = self.emp_name.parent_id.id
    	
    	    lis =[]
    	    for obj in self.emp_name.emp_memo_history_ids:
    	        lis.append((4,obj.id,))
    	    self.emp_memo_history_ids=lis or False
    	return {}
	      

    @api.multi
    def print_report(self):
       ''' Method called at 'Print' action in the Emp Memo History wizard.
	   Will print based on the Type selected.
       '''
       lis = []
       # Report type: Employee
       if self.report_type == 'employee' and self.emp_name :
           lis.append(self.emp_name.id)
           if not self.emp_name.emp_memo_history_ids:
               raise ValidationError('No records found.')
       # Report type: Department
       elif self.report_type == 'department' and self.department_id :
           emp_ids = self.env['hr.employee'].search([('department_id','=',self.department_id.id),('emp_memo_history_ids','!=',False)])
           if emp_ids:
               lis = emp_ids.ids
           else :
               raise ValidationError('No records found.')
       else:
           raise ValidationError('Please select any employee')
       datas = {
            'ids' : lis,
            'model' : 'hr.employee',
            }
       return {'type': 'ir.actions.report.xml','report_name':'employee_appraisal.report_memohistory','datas' : datas}


