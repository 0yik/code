from odoo import fields,models,api
from datetime import date,datetime

class HrEmployee(models.Model):
    _inherit="hr.employee"

    reviewer_id = fields.Many2one('hr.employee', 'Reviewer')

    @api.multi
    def create_appraisal(self):
        res = super(HrEmployee, self).create_appraisal()
        res['default_reviewer'] = self.reviewer_id.id
        return res

    @api.model
    def create(self, vals):
        employee = super(HrEmployee, self.with_context(consider_reviewer=False)).create(vals)
        if vals.get('reviewer_id'):
            self.env['supervisor.history.lines'].with_context(consider_reviewer=True).create({'supervisor_history_id':employee.id,'start_date':date.today(),'supervisor_name':vals['reviewer_id']})
        return employee
    
    @api.multi
    def write(self, vals):
        res = super(HrEmployee, self.with_context(consider_reviewer=False)).write(vals)
        if vals.get('reviewer_id'):
            for employee in self:            
                supervisor_obj = self.env['supervisor.history.lines']
                supervisor_ids = supervisor_obj.search([('supervisor_history_id','=',employee.id),('end_date','=',None)]) or False
                if supervisor_ids:
                    supervisor_ids.with_context(consider_reviewer=True).write({'supervisor_history_id':employee.id,'end_date':date.today()})
                supervisor_obj.with_context(consider_reviewer=True).create({'supervisor_history_id':employee.id,'start_date':date.today(),'supervisor_name':vals['reviewer_id']})
        return res

class employee_evaluation(models.Model):
    _inherit="employee.evaluation"

    @api.onchange('emp_id')
    def on_change_employee(self):  
        ''' Onchange over the field 'Employee' to populate the Department, EMP ID, reviewer and job title.'''  
        if self.emp_id:
            self.employee_id = self.emp_id.emp_id
            self.department_id = self.emp_id.department_id.id
            self.reviewer = self.emp_id.reviewer_id.id
            self.job_title = self.emp_id.job_id.id

class rating_lines(models.Model):
    _inherit="emp.rating.lines"

    def _get_rating_float(self):
        for rec in self:
            rec.rating_float = rec.rating.name and float(rec.rating.name) or 0.0

    rating_float = fields.Float('Rating', compute="_get_rating_float")

class SupervisorHistoryLines(models.Model):
    _inherit="supervisor.history.lines"


    def create(self, vals):
        if 'consider_reviewer' in self._context.keys():
            if not self._context['consider_reviewer']:
                return
        return super(SupervisorHistoryLines, self).create(vals)

    
    @api.multi
    def write(self, vals):
        if 'consider_reviewer' in self._context.keys():
            if not self._context['consider_reviewer']:
                return
        return super(SupervisorHistoryLines, self).write(vals)

