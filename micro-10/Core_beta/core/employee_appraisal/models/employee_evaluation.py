#-*- coding:utf-8 -*-
from odoo import fields,models,api, _
from odoo.exceptions import ValidationError, UserError
import odoo.addons.decimal_precision as dp
from datetime import date,datetime
from calendar import monthrange
from dateutil.relativedelta import relativedelta


class employee_evaluation(models.Model):
    _name="employee.evaluation"
    _description="Employee Evaluation"
    _rec_name = 'emp_id'

    emp_id=fields.Many2one('hr.employee',string="Employee Name")
    employee_id = fields.Char(string="Employee Id")
    job_title=fields.Many2one('hr.job',string="Job Title")
    reviewer=fields.Many2one('hr.employee',string="Reviewer")
#     year=fields.Many2one('year.config',string="Year")
    year=fields.Many2one('hr.year',string="Year")
    department_id=fields.Many2one('hr.department','Department')
    quarter=fields.Selection([  ('q1','Q1'),
                                ('q2','Q2'),
                                ('q3','Q3'),
                                ('q4','Q4'),
                             ],string="Quarter")

    status=fields.Selection([('draft','Draft'),('in_progress','In Progress'),('completed','Completed')], 'Status', default='draft')
    emp_rating_ids=fields.One2many('emp.rating.lines','emp_rating_id',string="")
    perf_for_quarter=fields.Float(string="Performance for the Quarter (%)", digits=dp.get_precision('Performance'),group_operator="avg")
    perf_for_year=fields.Float(string="Final Performance for the Year (%)", digits=dp.get_precision('Performance'))
    calculated_increment = fields.Float(string="Calculated Increment", digits=dp.get_precision('Performance'))
    final_increment = fields.Float(string="Final Increment", digits=dp.get_precision('Performance'))
    mngmt_roundoff = fields.Float(string="Management roundoff", digits=dp.get_precision('Performance'))
    final_salary = fields.Float(string="Final Salary", digits=dp.get_precision('Performance'))
    mngmt_comments = fields.Text('Management Comments', digits=dp.get_precision('Performance'))
    calculated_salary = fields.Float('Calculated Salary', digits=dp.get_precision('Performance'))
    current_salary = fields.Float('Current Salary', digits=dp.get_precision('Performance'))
    is_final_quarter = fields.Boolean('Is Final Quarter')
    is_year = fields.Boolean(string="Is Year")
    is_complete = fields.Boolean(string="Is Complete",default=False)

    emp_evaluation_ids = fields.One2many('employee.evaluation.history','emp_evaluation_id',string="Employee Evaluation History")
    

    @api.one
    @api.constrains('emp_id','year','quarter')
    def check_duplication(self):
	''' (Constraint) Method for Restricting duplicate records creation for an employee with same year and quarter.'''
        eval_obj = self.search([('id','!=',self.id),('emp_id','=',self.emp_id and self.emp_id.id or False),('year','=',self.year and self.year.id or False),('quarter','=',self.quarter)])
        if eval_obj:
            raise ValidationError('Duplication is not allowed for an employee with same year and quarter.')

    @api.onchange('emp_id')
    def on_change_employee(self):  
        ''' Onchange over the field 'Employee' to populate the Department, EMP ID, reviewer and job title.'''  
        if self.emp_id:
            self.employee_id = self.emp_id.emp_id
            self.department_id = self.emp_id.department_id.id
            self.reviewer = self.emp_id.parent_id.id
            self.job_title = self.emp_id.job_id.id

    @api.multi
    def dispay_overall_quarters(self):
        '''This method called from the Func evaluate().This is to display the Overall Rating TLM Users.'''
        test = []
        if self.quarter == 'q4':
            attendance_obj = self.env['hr.attendance']
            attendance_ids = []
            attendance_ids_q1 = attendance_obj.search([('employee_id','=',self.emp_id.id),('year','=',self.year.id),('month','in',['JAN','FEB','MAR'])])
            attendance_ids.append(attendance_ids_q1)
            attendance_ids_q2 = attendance_obj.search([('employee_id','=',self.emp_id.id),('year','=',self.year.id),('month','in',['APR','MAY','JUN'])])     
            attendance_ids.append(attendance_ids_q2)
            attendance_ids_q3 = attendance_obj.search([('employee_id','=',self.emp_id.id),('year','=',self.year.id),('month','in',['JUL','AUG','SEP'])])   
            attendance_ids.append(attendance_ids_q3)
            attendance_ids_q4 = attendance_obj.search([('employee_id','=',self.emp_id.id),('year','=',self.year.id),('month','in',['OCT','NOV','DEC'])])
            attendance_ids.append(attendance_ids_q4)
            ot_dic = {'name':'Total OT'}	
            tot_abs_dic = {'name':'Total Absent Hours'}         
            i = 1  
            for attendance_id in attendance_ids :
                tot_abs = 0.0
                ot = 0.0
                for att in attendance_id :
                    ot += att.ot
                    tot_abs += att.total_abs
                    ot_dic['quarter'+str(i)] = ot
                    tot_abs_dic['quarter'+str(i)] = tot_abs
                    i += 1

            dic = {}
            quarters_dic = {'q1':'quarter1','q2':'quarter2','q3':'quarter3','q4':'quarter4'}
            evaluation_objs = self.env['employee.evaluation'].search([('emp_id','=',self.emp_id.id),('year','=',self.year.id)]) or False
            if evaluation_objs:
                for eval_obj in evaluation_objs:
                   values_obtained = [(line.rating_label_id.name, line.rating.name) for line in eval_obj.emp_rating_ids if line.rating_label_id]
                   for tup in values_obtained:
                       if tup[0] in dic.keys():
                           dic[tup[0]].update({'name':tup[0], quarters_dic[eval_obj.quarter]:tup[1]})
                       else:
                           dic[tup[0]] = {'name':tup[0], quarters_dic[eval_obj.quarter]:tup[1]}
                evaluation_history = self.env['employee.evaluation.history']
                for  val in dic.values():
                    history_id = evaluation_history.create(val)
                    test.append(history_id.id)
            
            history_id = evaluation_history.create(ot_dic)
            test.append(history_id.id)
            history_id = evaluation_history.create(tot_abs_dic)
            test.append(history_id.id)
                  
            self.emp_evaluation_ids = [(6,0,test)]
        else:
            self.emp_evaluation_ids = [(6,0,test)]
            
    
    @api.multi
    def evaluate(self):
        """ Method called on 'Evaluate' button action.This will calculate the Quarter performance.
	    Each step of operation is described in the method defnition.
	 """        
        manager_group_id = self.env['ir.model.data'].get_object_reference('hr', 'group_hr_manager')[1]
        tlm_group_id = self.env['ir.model.data'].get_object_reference('employee_appraisal', 'top_level_manager')[1]
        admin_group_id = self.env['ir.model.data'].get_object_reference('base', 'group_system')[1]
        user_obj = self.env['res.users'].browse(self.env.uid)
        group_ids = []
        for grp in user_obj.groups_id:
            group_ids.append(grp.id)
        if manager_group_id in group_ids and tlm_group_id not in group_ids and admin_group_id not in group_ids:
            raise ValidationError(' HR Manager is not allowed to do the evaluation process.')

        if self.quarter == 'q2':
             eval_obj = self.env['employee.evaluation'].search([('emp_id','=',self.emp_id.id),('employee_id','=',self.employee_id),('year','=',self.year.id),('quarter','=','q1')]) or False
             if (not eval_obj or eval_obj.status == 'draft'):
                raise ValidationError(' Q1 evaluation is not completed to this ' +self.emp_id.name+ ' employee for ' +self.year.name+ ' year ')

        elif self.quarter == 'q3':
             eval_obj = self.env['employee.evaluation'].search([('emp_id','=',self.emp_id.id),('employee_id','=',self.employee_id),('year','=',self.year.id),('quarter','=','q2')]) or False
             if (not eval_obj or eval_obj.status == 'draft'):
                raise ValidationError(' Q2 evaluation is not completed to this ' +self.emp_id.name+ ' employee for ' +self.year.name+ ' year ')

        elif self.quarter == 'q4':
             eval_obj = self.env['employee.evaluation'].search([('emp_id','=',self.emp_id.id),('employee_id','=',self.employee_id),('year','=',self.year.id),('quarter','=','q3')]) or False
             if (not eval_obj or eval_obj.status == 'draft'):
                raise ValidationError(' Q3 evaluation is not completed to this ' +self.emp_id.name+ ' employee for ' +self.year.name+ ' year ')
        
        sal_history_pool = self.env['salary.history']
        sal_history_lines = self.env['salary.history.lines']
        sal_band_pool = self.env['salary.band']
        attend_pool = self.env['hr.attendance']
        rating_val_pool = self.env['rating.values']
        
        emp_department = self.emp_id.department_id
        ratings_weight = {}
        for rating in emp_department.weightage_line_ids:
            ratings_weight[rating.rating_id] = rating.weightage
        if not ratings_weight:
            raise ValidationError("Please define Ratings & Weightages for the department '"+emp_department.name+"'. Please contact the HR Manager.")
        elif ratings_weight and sum(ratings_weight.values()) == 0:
            raise ValidationError("Please define the weightage for atleast one Rating. Seems the total weightage is zero for the Department '"+emp_department.name+"'. Please contact the HR Manager.")

        perf_for_quarter = 0.0 ## Performance for the Quarter (%)
        perf_for_year = 0.0  ##  Final Performance for the Year (%) 
        salary_increased = 0   ## Increased Salary     
        
        ### Calculate the Attendance %
        qua_months = {'q1':['JAN','FEB','MAR'],'q2':['APR','MAY','JUN'],'q3':['JUL','AUG','SEP'],'q4':['OCT','NOV','DEC']}
        qua_month_int = {'q1':[1,2,3],'q2':[4,5,6],'q3':[7,8,9],'q4':[10,11,12]}
        months = qua_months.get(self.quarter)
        month_ints = qua_month_int.get(self.quarter)
        total_days = 0.0
        for i in month_ints:
            no_of_days = monthrange(int(self.year.name), i)[1]
            total_days += no_of_days
        
        # To get the record ids from Attendance master
        attend_objs = attend_pool.search([('employee_id','=',self.emp_id.id),('year','=',self.year.id),('month','in',months)], limit=3, order="id desc") or False
        
        ph_rest_days = 0.0
        absent_days = 0.0
        if attend_objs:
            for obj in attend_objs:
                ph_rest_days += obj.ph + obj.rest
                absent_days += obj.total_abs
            total_wrk_days = total_days - (ph_rest_days)
            if absent_days > total_wrk_days:
                raise ValidationError('Give proper attendance data. Here Absent days is greater than working days for this quarter. Please contact the HR Manager.')
            attendance_perc = ((total_wrk_days-absent_days)/total_wrk_days) * 100  # Attendance %
            attendance_perc = round(attendance_perc,1)  # Attendance %
        else:
            attendance_perc = 0.0
        ### Ends
        
        ### Calculate Performance for the Quarter (%)
        for rate_line in self.emp_rating_ids:
            rate_line.stop_process = False 
            if not ratings_weight.has_key(rate_line.rating_label_id):
                raise ValidationError("Rating label '"+rate_line.rating_label_id.name+"' is not tagged to the department '"+emp_department.name+"'. Please contact the HR Manager.")
            full_score = 0
            ## To get the FULL score of the department
            for dept in rate_line.rating_label_id.rating_ids:
                if dept.department_id.id == self.department_id.id:
                    if dept.score == 0:
                        raise ValidationError("Full score is zero for the Rating label '"+rate_line.rating_label_id.name+"'. Please contact the HR Manager.")
                    else:
                        full_score = dept.score
                    break;
            ## Ends
#             if rate_line.rating_label_id.name == 'Attendance':
#                 score_ids = rating_val_pool.search([('department_id','=',self.department_id.id),('rating_id','=',rate_line.rating_label_id.id),('name','<=',str(full_score))])
#                 ranges = [float(sco.name) for sco in score_ids]
#                 range_ids = [sco.id for sco in score_ids]
#                 
# 
#                 att_objs = self.env['attendance.percentage'].search([])
#                 rating_val = False
#                 for obj in att_objs:
#                     if attendance_perc >= obj.from_val and attendance_perc <= obj.to_val:
#                         rating_val = obj.rating
#                 if isinstance(rating_val, bool) and not rating_val:
#                     raise ValidationError("Please configure the Attendance Percentage master properly. Please contact the HR Manager.")		
#                 rating_id = False
#                 if not rating_val in ranges:
#                     raise ValidationError("The record with Rating "+str(rating_val)+" in the Attendance Percentage master is greater than Full Score of the Attendance Label. Please contact the HR Manager.")
#                 index = ranges.index(rating_val)
#                 rating_id = range_ids[index]
#                 if rating_id:
#                     rate_line.rating = rating_id
#                 perf_for_quarter += ((rating_val)/full_score * ratings_weight[rate_line.rating_label_id])
            if float(rate_line.rating.name) > 0:
                perf_for_quarter += ((float(rate_line.rating.name))/full_score * ratings_weight[rate_line.rating_label_id])
        ### Ends 
        ### To get the Current Salary fetching from the Salary history master.
        curr_salary = self.emp_id.current_salary
        if curr_salary == 0:
            raise ValidationError("Current Salary of the Employee is not defined. Please contact the HR Manager.")
        ### Ends

        ### Finding the Max Increment for the Current Salary from the Salary Band Master  
        sal_band = sal_band_pool.search([('department_id','=',self.emp_id.department_id.id)], limit=1, order="id desc") or False
        if not sal_band:
            raise ValidationError("Salary band for the Department '"+self.emp_id.department_id.name+"' is not defined. Please contact the HR Manager.")
        if not sal_band.salaryrange_ids:
            raise ValidationError("Salary Range & Increments for the Department '"+self.emp_id.department_id.name+"' is not defined. Please contact the HR Manager.")
        max_incre = 0.0 
        for obj in sal_band.salaryrange_ids:
            if int(curr_salary) in range(obj.from_val, obj.to_val+1):
                max_incre = obj.max_increment  # Max Increment %
                break;
        if max_incre == 0:
            raise ValidationError("Define the proper Salary Range & Increments in the Salary Band master. Please contact the HR Manager.")
        ### Ends

        ### Calc Increased Salary and Increase %
        status = 'draft'
        is_final_quarter = False
        if self.quarter == 'q4':
            self.dispay_overall_quarters()
            is_final_quarter = True
            status = 'in_progress'
            ### Calculate Final Performance of the year, for the final quarter.
            evaluations = self.search([('emp_id','=',self.emp_id.id),('year','=',self.year.id),('quarter','in',('q1','q2','q3')),('status','=','completed')]) or False
            if evaluations:
                quarter_values = [obj.perf_for_quarter for obj in evaluations]
                total_quart = len(quarter_values) + 1
                if not quarter_values:
                     perf_for_year = perf_for_quarter
                else:
                    total_quarters_value = reduce(lambda a,b: a+b, quarter_values) + perf_for_quarter
                    perf_for_year = total_quarters_value/total_quart
            else:
                perf_for_year = perf_for_quarter
            ###  Ends 
            salary_increased = curr_salary * (max_incre/100) * (perf_for_year/100) # Increased Salary
            cal_increment = (((salary_increased + curr_salary) - curr_salary)/curr_salary) * 100 # Salary Increased %
        
        self.write({'current_salary':self.emp_id.current_salary,'perf_for_quarter':perf_for_quarter,'perf_for_year':perf_for_year,'calculated_increment':salary_increased,
                    'calculated_salary':(salary_increased + curr_salary),'status':status,'final_increment':salary_increased,
                    'final_salary':(salary_increased + curr_salary),'is_final_quarter':is_final_quarter,
                    })

    @api.onchange('mngmt_roundoff')
    def onchange_mngmt_round(self):
        ''' On change over the field 'Management roundoff'.
            Will return the Final Increment and Final Salary.
	'''
        if self.calculated_increment > 0:
            cal_sal = self.calculated_increment
            final_inc = self.mngmt_roundoff + cal_sal
            self.final_increment = final_inc
            self.final_salary = self.mngmt_roundoff + self.calculated_salary  

    @api.multi
    def reevaluate(self):
	''' Method called from the Re Evaluate button action.
	    This will make the state to "Draft', Performance for the Quarter to '0.0' and clears the Employee Evaluation History.
	'''
        if self.status == 'completed' or self.status == 'in_progress':
            self.status = 'draft'
            self.perf_for_quarter = 0.0    
	    self.emp_evaluation_ids = [(6,0,[])]
    
    @api.multi
    def completed_evaluation(self):
        ''' Method called at On click on  'Evaluation Complete' button. 
            Will set the status to Completed and update the History in the Employee master.
	''' 
        for obj in self.emp_rating_ids:
            if obj.stop_process:
                raise ValidationError("Rating '"+str(obj.rating_label_id and obj.rating_label_id.name or '')+"' is changed. Please update the evaluation before proceeding to complete.")
        if self.quarter == 'q4':
            tlm_group_id = self.env['ir.model.data'].get_object_reference('employee_appraisal', 'top_level_manager')[1]

            user_obj = self.env['res.users'].browse(self.env.uid)
            group_ids = []
            for grp in user_obj.groups_id:
                group_ids.append(grp.id)
            if tlm_group_id not in group_ids :
                raise ValidationError('Only Top Level Manager user can complete evaluation process for Q4 quarter by giving management round off')
            if self.status == 'draft' and self.perf_for_quarter == 0:
                raise ValidationError("Please update the Performance for the Quarter. Click on 'Evaluate' to start calculations.")
            if self.final_salary == 0:
                raise ValidationError("Please update the Final Salary. Click on 'Evaluate' to start calculations.")
            curr_sal = self.emp_id.current_salary
            fin_sal = self.final_salary
            inc_per = float(((fin_sal-curr_sal)/curr_sal)*100)
            if self.emp_id.salary_history_ids:
                for obj in self.emp_id.salary_history_ids:
                    if not obj.end_date:
                        obj.end_date = date.today()
            self.emp_id.write({'current_salary':self.final_salary,'salary_history_ids':[(0,0,{'salary':self.final_salary, 'start_date':date.today(),'year':self.year.id,'increment':inc_per})]})
            self.is_complete = True
            objs = self.env['employee.evaluation'].search( [('emp_id','=',self.emp_id.id),('employee_id','=',self.employee_id),('year','=',self.year.id),('quarter','in',['q1','q2','q3'])],limit=3)
            for obj in objs:
                obj.is_complete = True
        else:
            if self.perf_for_quarter == 0:
                raise ValidationError("Please update the Performance for the Quarter. Click on 'Evaluate' to start calculations.")
            
        # To write the status in the Emp History.
        emp_obj = self.emp_id
        dic = {'job_title':self.job_title.id,'reviewer':self.reviewer.id,'perf_of_quarter':self.perf_for_quarter, 'status':'completed',
              }
                
        self.status = 'completed'
        
        
    @api.multi
    def open_memo(self):
        ''' Method called from the button 'Memo' and Opens the Memo master to view the Memo history of the Employee.'''
	memo_obj = self.env['employee.memo'].search([('emp_name','=',self.emp_id.id)])
	if memo_obj:
            view_id = self.env['ir.model.data'].get_object_reference('employee_appraisal', 'emp_memo_history_form_view')[1]
            return {
                'name':'Employee Memo History',
                'nodestroy':True,                
                'view_id':view_id,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'emp.memo.history',
                'type': 'ir.actions.act_window',
                'target':'new',
                'context':{'default_report_type':'employee','default_emp_name':self.emp_id.id,'default_is_memo_button':True} }
        else:
            raise ValidationError("Memo not created for this employee ")
    

    @api.multi
    def unlink(self):
        ''' Method overridden for restricting records deletion other than Draft State.'''
        for obj in self:
            if not obj.status == 'draft':
                raise ValidationError("Not allowed to delete the record other than draft state.")
        return super(employee_evaluation, self).unlink()

    def _get_values(self):
	''' Method called from the Evaluation report.'''
        eval_obj = self.search([('emp_id','=',self.emp_id.id),('year','=',self.year.id)])
        values_list = []
        for obj in eval_obj:
            if obj.quarter == 'q4':
                values_list.extend((obj.current_salary,obj.final_increment,obj.final_salary,obj.perf_for_year))
        if not values_list:
            values_list.extend( (0.0,0.0,0.0,0.0) )
        return values_list

    def _get_details(self):
	''' Method called from the Evaluation report.'''
        eval_obj = self.search([('emp_id','=',self.emp_id.id),('year','=',self.year.id)])
	rating = self.env['rating.config'].search([])
        rating_list = []
	rating = []
	q = ['q1','q2','q3','q4']
        for obj in eval_obj:
	    q.append(obj.quarter)
	    for line in obj.emp_rating_ids:
		if line.rating_label_id.name not in rating :
		    rating.append(line.rating_label_id.name)	
	for label in rating :
	    record = []
	    record.append(label)
	    for val in q :
		obj = self.search([('emp_id','=',self.emp_id.id),('year','=',self.year.id),('quarter','=',val)])
		check = []
		
		if obj :
		    for line in obj.emp_rating_ids:
		        check.append(line.rating_label_id.name)
		        if label == line.rating_label_id.name :
			    record.append(line.rating.name)
			    record.append(line.comment)
		    if label not in check :
		        record.append(0)
		        record.append(' ')
		else :
		    record.append(0)
                    record.append(' ')
	    rating_list.append(record) 
        return rating_list

class rating_lines(models.Model):
    _name="emp.rating.lines"
    _description="Employee Evaluation Rating Lines"

    @api.depends('emp_rating_id')
    def _get_rating_calculation(self):
        for record in self:
            employee_ids = self.env['employee.evaluation'].search([('emp_id', '=', record.employee_id.id)])
            for employee_id in employee_ids:
                total_records = 0
                total_ratings = 0
                full_score = 0
                for evaluation in employee_id.emp_rating_ids:
                    if evaluation:
                        total_records += 1
                        total_ratings += float(evaluation.rating.name)
                        full_score += 5
                total = float(total_records)
                ratings = float(total_ratings)
                if total > 0.00:
                    record.average_rating = ratings / total

    @api.depends('rating')
    def _get_ratings(self):
        for record in self:
            if record.rating:
                record.ratings = float(record.rating.name)

    quarter=fields.Selection(related='emp_rating_id.quarter', string="Quarter", store=True)

    rating_label_id=fields.Many2one('rating.config',string="Rating Labels")
    rating = fields.Many2one('rating.values', 'Rating')
    comment=fields.Text(string="Comments")
    emp_rating_id=fields.Many2one('employee.evaluation',string="Rating")
    eval_report_rating_id=fields.Many2one('evaluation.report',string="")
    perf_report_rating_id=fields.Many2one('performance.report',string="")
    emp_perf_rating_id=fields.Many2one('employee.performance',string="")
    is_attendance_type = fields.Boolean('Is Attendance Type')
    full_score = fields.Many2one('rating.values','Full Score')
    stop_process = fields.Boolean('Stop Process') # Will be set when there is a change on the 'rating' field.
    employee_id = fields.Many2one('hr.employee', related='emp_rating_id.emp_id', string='Employee', store=True)
    status = fields.Selection(related='emp_rating_id.status', string='Status', store=True)
    average_rating = fields.Float(compute='_get_rating_calculation', string='Average Rating', store=True)
    ratings = fields.Float(compute='_get_ratings', string='Ratings', store=True)

    @api.onchange('rating')
    def onchange_rating(self):
        ''' Onchange over the 'Rating' field shall always set the field 'Stop Process' field as True.'''
        context = dict(self.env.context or {})
        if context.get('eval_rating_id'):
            self.stop_process = True



class employee_evaluation_history(models.Model):
    _name="employee.evaluation.history"
    _description="Employee Evaluation History"

    @api.depends('quarter1','quarter2','quarter3','quarter4')
    def _get_average(self):
	''' Method of a computational field.
	    Will calculate the average of the four quarters.
	'''
	for his in self :
		if his.quarter1 or his.quarter2 or his.quarter3 or his.quarter4 :
			avg = (his.quarter1 + his.quarter2 + his.quarter3 + his.quarter4)/4
			his.average = avg
		else :
			his.average = 0.0

    name = fields.Char('Name')
    quarter1 = fields.Float('Q1')    
    quarter2 = fields.Float('Q2')
    quarter3 = fields.Float('Q3')
    quarter4 = fields.Float('Q4')
    average = fields.Float(string = 'Average',compute = "_get_average")
    emp_evaluation_id = fields.Many2one('employee.evaluation',string="Rating")
