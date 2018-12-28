# -*- coding: utf-8 -*- 
from odoo import fields, models, api
from odoo.osv import osv
from odoo.tools.translate import _
from odoo.exceptions import UserError, RedirectWarning, ValidationError
from datetime import date,datetime
from odoo.http import request
import re


class hr_employee(models.Model):
    _inherit="hr.employee"
    
    @api.multi
    def _get_login_user(self):
        """(Method called from a Computed Field 'is_login_user').
           Sets the field 'is_login_user' according to conditions as below. """
        users = [user.id for user in self.env.ref('hr.group_hr_manager').users]
        users += [user.id for user in self.env.ref('employee_appraisal.top_level_manager').users]
	uid = self.env.user.id
        for obj in self:
            if uid != 1 and not uid in users: # (Condition1 : If current user is not admin and not in HR Manager, TLM groups)
                obj.is_login_user = (obj.user_id.id == uid)
            else:                             # (Else: Sets to True)
                obj.is_login_user = True


    emp_id = fields.Char('Employee ID')
    end_date = fields.Date('End Date')
    education_qual_id = fields.Many2one('education.qualification','Education Qualification')
    emg_contact_name = fields.Char(string="Emergency Contact Name")
    emg_contact_no_code = fields.Char(string="Emergency Contact Number Code",size=3)
    emg_contact_no = fields.Char(string="Emergency Contact Number")
    #bank_account_id = fields.Char(string="Bank Account Number")
    bank_account_id = fields.Many2one('res.partner.bank', string='Bank Account Number',
        domain="[('partner_id', '=', address_home_id)]", help='Employee bank salary account')
    bank_acc = fields.Char(string="Bank Account")
    status = fields.Selection([('casual','Casual'),
                               ('new_hire','New Hire'),
                               ('permanent','Permanent'),
                               ('terminated','Terminated'),
                              ],string='Employee Status')

    department_history_ids = fields.One2many('department.history.lines','department_history_id',string="")
    salary_history_ids = fields.One2many('salary.history.lines','salary_history_id',string="")
    supervisor_history_ids = fields.One2many('supervisor.history.lines','supervisor_history_id',string="")
    emp_status_history_ids = fields.One2many('employee.history.lines','emp_status_history_id',string="")
    evaluation_ids = fields.One2many('employee.evaluation','emp_id',string="")
    is_login_user = fields.Boolean(compute = _get_login_user,  string="Is Login User",
                                        help="Check whether the Employee is a current logged in user.")
    shift_id = fields.Char('Shift ID')
    other_id = fields.Char('Other ID')
    active = fields.Boolean('Active', default=True)
    current_salary = fields.Float("Current Salary(Per Annum)")
    emp_memo_history_ids = fields.One2many('employee.memo','emp_name',string='Employee Memo History')
   
    _sql_constraints = [('emp_id_uniq','unique(emp_id)','The Employee Id must be unique.')]
    

#     @api.onchange('birthday','joining_date')
#     def onchange_dates(self):
#         ''' On Change func() on DOB and Joining Date fields performing validations to restrict the user entering the future dates.'''
# #         formt_date, res = False, {'value':{},'warning':{'title':'Warning!','message':'Future Dates are not allowed.'}}
#         formt_date, res = False, {'value':{}}
#         if self.env.context.has_key('birthday'):
#             formt_date = datetime.strptime(self.birthday,"%Y-%m-%d")
#         elif self.env.context.has_key('joining_date'):
#             formt_date = datetime.strptime(self.joining_date,"%Y-%m-%d")
#         if formt_date and datetime.today() < formt_date:
#             if self.env.context.has_key('joining_date'):
#    	            self.joining_date = False
#             else:
#                 self.birthday = False
#         return res
# 	return {}

    @api.onchange('mobile_phone','work_phone')
    def onchange_phone_no(self):
	''' On Change func() on Work Phone and Work Mobile fields performing validations to restrict the user entering the irregular formats.'''
	phone_no, res = False, {'value':{},'warning':{'title':'Warning!','message':"Please note that Characters are not allowed except '+'.(For eg:[+xx] xxxxxxxxxx)."}}
	if self.env.context.has_key('mobile_phone'):
	    phone_no = self.mobile_phone
	elif self.env.context.has_key('work_phone'):
            phone_no = self.work_phone
    	if phone_no and not (re.match("^[+][\\0-9]*$",phone_no) or re.match("^[0-9]*$",phone_no)):
	    if self.env.context.has_key('mobile_phone'):
		self.mobile_phone = False
	    else:
		self.work_phone = False
	    return res
	return {}
	    

    @api.onchange('emg_contact_no_code')
    def onchange_contact_code(self):
        ''' On Change func() on Emergency Contact Code fields performing validations to restrict the user entering the irregular formats.'''
        phone_no, res = False, {'value':{},'warning':{'title':'Warning!','message':"The format should be '+xx' x must be a digit !"}}
        phone_no = self.emg_contact_no_code
        if phone_no and not (re.match("^[+][\\0-9]*$",phone_no)):
            self.emg_contact_no_code = False
            return res
        return {}
        
    @api.onchange('emg_contact_no')
    def onchange_contact(self):
        ''' On Change func() on Emergency Contact Number to check the validations.'''
        phone_no, res = False, {'value':{},'warning':{'title':'Warning!','message':"Only Integers are allowed at emergency contact number."}}
        phone_no = self.emg_contact_no
        if phone_no and not (re.match("^[0-9]*$",phone_no)):
            self.emg_contact_no = False
            return res
        return {}        

    @api.model
    def create(self, vals):
        ''' Method Overriden to update the History of  Salary, Supervisor, Department.'''
	## To create the Salary History ##
        if vals.has_key('current_salary'):
            sal = vals.get('current_salary')
            if sal > 0:
                year = datetime.now().strftime("%B %d-%Y").split('-')[1]
                year_id = self.env['hr.year'].search([('name','=',year)]) or False
                if not year_id:
                    raise ValidationError("Please define the year '"+year+"' under the Year master.")
                vals.update({'salary_history_ids':[(0,0,{'salary':sal,'start_date':date.today(),'year':year_id.id})]})
        new_id =  super(hr_employee, self).create(vals)
	
	## To Create the Department History ##	
        if vals.get('department_id'):
            self.env['department.history.lines'].create({'department_history_id':new_id.id,'start_date':date.today(),'department_id':vals['department_id']})
	## TO Create the Supervisor history ##
        if vals.get('parent_id'):
            self.env['supervisor.history.lines'].create({'supervisor_history_id':new_id.id,'start_date':date.today(),'supervisor_name':vals['parent_id']})
	## To Create the Status History. ##
        dic = {'casual':'Casual','new_hire':'New Hire','permanent':'Permanent','terminated':'Terminated'}
        if vals.get('status'):
            print "======vals['status']==============",vals['status']
            self.env['employee.history.lines'].create({'start_date':date.today(),'emp_status_history_id':new_id.id,'emp_status':dic[vals['status']]})
        return new_id

    
    @api.multi
    def write(self, vals):
        ''' Method overriden To update the History of  Salary, Supervisor, Department details.'''
        print "==============here======="
        for obj in self:
	    ## To create the Salary history line. ##
            if vals.has_key('current_salary'):
                sal = vals.get('current_salary')
                if not obj.salary_history_ids:
                    year = datetime.now().strftime("%B %d-%Y").split('-')[1]
                    year_id = self.env['hr.year'].search([('name','=',year)]) or False
                    print "========year_id===============",year_id
                    if not year_id:
                        raise ValidationError("Please define the year '"+year+"' under the Year master.")
                    vals.update({'salary_history_ids':[(0,0,{'salary':sal,'start_date':date.today(),'year':year_id.id})]})
	    ## To Create/update the Department history line. ##
            if vals.has_key('department_id'):
                dept_obj = self.env['department.history.lines']
                dept_ids = dept_obj.search([('department_history_id','=',obj.id),('end_date','=',None)]) or False
                if not dept_ids :
                    dept_obj.create({'department_history_id':obj.id,'start_date':date.today(),'department_id':vals['department_id']})
                else:
                    dept_id = dept_ids[0].department_id.id
                    if dept_id and dept_id != vals['department_id']:
                        dept_ids.write({'department_history_id':obj.id,'end_date':date.today()})
                        dept_obj.create({'department_history_id':obj.id,'start_date':date.today(),'department_id':vals['department_id']})
	    ## To Create/update the Supervisor history line. ##
            if vals.has_key('parent_id'):
                supervisor_obj = self.env['supervisor.history.lines']
                supervisor_ids = supervisor_obj.search([('supervisor_history_id','=',obj.id),('end_date','=',None)]) or False
                if supervisor_ids :
                    supervisor_ids.write({'supervisor_history_id':obj.id,'end_date':date.today()})
                supervisor_obj.create({'supervisor_history_id':obj.id,'start_date':date.today(),'supervisor_name':vals['parent_id']})
	    ## To Create/update the Status history lines. ##
            if vals.has_key('status'):
                emp_status_obj = self.env['employee.history.lines']
                emp_status_ids = emp_status_obj.search([('emp_status_history_id','=',obj.id),('end_date','=',None)]) or False
                if emp_status_ids :
                    emp_status_ids.write({'emp_status_history_id':obj.id,'end_date':date.today()})
                dic = {'casual':'Casual','new_hire':'New Hire','permanent':'Permanent','terminated':'Terminated'}
                emp_status_obj.create({'start_date':date.today(),'emp_status_history_id':obj.id,'emp_status':dic[vals['status']]})
        return super(hr_employee, self).write(vals)


    
    @api.multi
    def create_appraisal(self):
        ''' On Click at Create Appraisal to create the Evaluation manually.'''
        lis =[]
        for rec in self.department_id.weightage_line_ids :
            if rec:
                if rec.rating_id.name == 'Attendance':
                    is_attendance_type = True
                else:
                    is_attendance_type = False

                rating_obj = self.env['rating.config'].search([('name','=',rec.rating_id.name)])
                for line in rating_obj.rating_ids:
                    if line.department_id == self.department_id:
                        score = line.score
                request.cr.execute("select min(name) from rating_values where department_id=%d and rating_id=%d"%(self.department_id.id,rec.rating_id.id))
                value = request.cr.fetchone()
                min_scr_obj = self.env['rating.values'].search([('name','=',value[0]),('department_id','=',self.department_id.id),('rating_id','=',rec.rating_id.id)],limit=1)
                obj = self.env['rating.values'].search([('name','=',score),('department_id','=',self.department_id.id),('rating_id','=',rec.rating_id.id)])

                dic = {'rating_label_id' : rec.rating_id.id,'is_attendance_type':is_attendance_type,'rating':min_scr_obj.id,'full_score':obj.id}
                lis.append((0,0,dic))
        if not lis:
            raise ValidationError("Cannot create the Appraisal as there are no ratings configured for the department '"+self.department_id.name+"'.")
        view_id = self.env['ir.model.data'].get_object_reference('employee_appraisal','emp_eval_form_view')[1]
        return {'name': 'Create Appraisal',
            'nodestroy' : True,
            'view_id' : view_id,
            'view_type' : 'form',
            'view_mode' : 'form',
            'res_model' : 'employee.evaluation',
            'type' : 'ir.actions.act_window',
            'context' : {'default_emp_id' : self.id,'default_employee_id':self.emp_id,'default_department_id' : self.department_id.id,'default_reviewer' : self.parent_id.id,'default_job_title' : self.job_id.id,'default_emp_rating_ids' : lis}
            }    


class DepertmentHistoryLines(models.Model):
    _name="department.history.lines"


    department_id = fields.Many2one('hr.department',string="Department name")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    department_history_id = fields.Many2one("hr.employee",string="")

class SalaryHistoryLines(models.Model):
    _name="salary.history.lines"

    salary = fields.Float(string="Salary")
    currency = fields.Many2one('res.currency',string="Currency",default = lambda self:self.env['res.users'].browse(self.env.user.id).company_id.currency_id.id)
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End date")
    salary_history_id = fields.Many2one('hr.employee',string="")
    year = fields.Many2one('hr.year',string='Year')
    increment = fields.Float(string='Increment%')
    salary_history_wizard_id = fields.Many2one('salary.history',string='')

    

class SupervisorHistoryLines(models.Model):
    _name="supervisor.history.lines"
    _description = "Supervisor History"

    supervisor_name = fields.Many2one('hr.employee',string="Supervisor name")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    supervisor_history_id = fields.Many2one('hr.employee',string="")


class EmployeeHistoryLines(models.Model):
    _name="employee.history.lines"
    _description = "Employee Status History"


    emp_status = fields.Char(string="Employee status")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    emp_status_history_id = fields.Many2one('hr.employee',string="")

