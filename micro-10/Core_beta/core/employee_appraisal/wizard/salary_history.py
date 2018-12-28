# -*- coding: utf-8 -*-
from odoo import fields,models,api
from odoo.exceptions import ValidationError

class salary_history(models.Model):
    _name="salary.history"
    _rec_name = 'emp_name'
    
    emp_name=fields.Many2one('hr.employee',string="Employee Name")
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


    salary_history_ids = fields.One2many('salary.history.lines','salary_history_wizard_id',string='Salary History Lines')
    
    report_type = fields.Selection([('employee','Employee'),('department','Department')],string='Report Type')    



    @api.onchange('emp_name')
    def onchange_name(self):
        ''' Onchange over Employee to populate the EMP ID, job, join date, department, supervisor, emp status.'''
        if self.emp_name:
            self.emp_id = self.emp_name.emp_id
            self.job_title = self.emp_name.job_id.id
            self.join_date = self.emp_name.join_date
            self.department_id = self.emp_name.department_id.id
            self.supervisor_name= self.emp_name.parent_id.id
            self.emp_status = self.emp_name.status
            lis = []
            for rec in self.emp_name.salary_history_ids:
                val = { 'salary':rec.salary,'currency':rec.currency.id,'start_date':rec.start_date,'year':rec.year.id,'increment':rec.increment,'end_date':rec.end_date}
                lis.append((0,0,val))
            self.salary_history_ids = lis 
        return {}
        

    @api.multi
    def print_report(self):
        ''' Method called from the 'Print' button action in the wizard of salary history report.
	    Will Print based on the Type selected.
	'''
        lis = []
        # Report type: Employee
        if self.report_type == 'employee' and self.emp_name and self.department_id:
            lis.append(self.emp_name.id)
            if not self.salary_history_ids:
                raise ValidationError('No records found.')      
        # Report type: Department
        elif self.report_type == 'department' and self.department_id:
            emp_ids = self.env['hr.employee'].search([('department_id','=',self.department_id.id),('salary_history_ids','!=',False)])
            if emp_ids:
                lis = emp_ids.ids
            else :
                raise ValidationError('No records found.')
        if not lis:
            raise ValidationError('No records found.')      
        datas = { 'ids' : lis,
                  'model' : 'hr.employee',
                }
        return { 'type' : 'ir.actions.report.xml', 'report_name' : 'employee_appraisal.report_salaryhistory_id', 'datas': datas }
