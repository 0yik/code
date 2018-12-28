# -*- coding: utf-8 -*-
import time
from datetime import date, datetime
from odoo import fields, models, exceptions, api, _
from odoo.exceptions import UserError
import calendar
from datetime import timedelta

class EmsClass(models.Model):
    _inherit = 'ems.class'
    
    student_ids = fields.One2many('ems.class.student.line', 'ems_id','Students')
    
    @api.multi
    @api.onchange('intake_id')
    def onchange_intake_id(self):
        student_obj = self.env['student.student']
        student_list = []
        for rec in self:
            if rec.intake_id:
                student_ids = student_obj.search([('year', '=',rec.intake_id.id),('state', '=', 'done')])
                for student in student_ids:
                    student_list.append({
                    	'roll_no': student.roll_no,
                        'student_id': student.id,
                        'is_present': True
                    })
            rec.student_ids = student_list
            
    
    @api.multi
    def generate_recurrent(self):
        if self.recurrency:
            hr_holiday_lines_pool = self.env['hr.holiday.lines']
            #ems_class_ids = []
            interval = self.interval
            start_time = datetime.strptime(self.start_time, '%Y-%m-%d %H:%M:%S')
            end_time = datetime.strptime(self.end_time, '%Y-%m-%d %H:%M:%S')
            end_type = self.end_type
            if end_type == 'end_date':
                final_date = datetime.strptime(self.final_date, '%Y-%m-%d %H:%M:%S')
                while start_time < final_date:
                    new_start_date = start_time + timedelta(days=interval)
                    new_end_date = end_time + timedelta(days=interval)
                    # Exclude Weekend
                    weekday = new_start_date.weekday()
                    if self.exclude_weekend:
                        if weekday == 5:
                            new_start_date = start_time + timedelta(days=interval+2)
                            new_end_date = end_time + timedelta(days=interval+2)
                        if weekday == 6:
                            new_start_date = start_time + timedelta(days=interval+1)
                            new_end_date = end_time + timedelta(days=interval+1)
                    
                    # Exclude Public Holiday
                    if self.exclude_public:
                        #print "\n\n======new_start_date==",new_start_date
                        date_dict = self.exclude_public_holiday(new_start_date,new_end_date,interval)
                        if date_dict.has_key('new_start_date'):
                            #print "\n\n###new_start_date=",date_dict['new_start_date']
                            str_date = date_dict['new_start_date'].strftime('%Y-%m-%d')
                            hr_holiday_lines_objs =  hr_holiday_lines_pool.search([('holiday_date','=',str_date)])
                            if hr_holiday_lines_objs:
                                date_dict = self.exclude_public_holiday(new_start_date,new_end_date,interval)
                                new_start_date = date_dict['new_start_date']
                                new_end_date = date_dict['new_end_date']
                                #print "\n\n===new_start_date=",new_start_date,new_end_date
                            else:
                                new_start_date = date_dict['new_start_date']
                                new_end_date = date_dict['new_end_date']
                                weekday = new_start_date.weekday()
                                if weekday == 5:
                                    new_start_date = new_start_date + timedelta(days=2)
                                    new_end_date = new_end_date + timedelta(days=2)
                                if weekday == 6:
                                    new_start_date = new_start_date + timedelta(days=1)
                                    new_end_date = new_end_date + timedelta(days=1)
                                #print "\n\n******new_start_date=",new_start_date,new_end_date
                                str_date = new_start_date.strftime('%Y-%m-%d')
                                hr_holiday_lines_objs =  hr_holiday_lines_pool.search([('holiday_date','=',str_date)])
                                if hr_holiday_lines_objs:
                                    date_dict = self.exclude_public_holiday(new_start_date,new_end_date,interval)
                                    new_start_date = date_dict['new_start_date']
                                    new_end_date = date_dict['new_end_date']
                    #####
                    start_time = new_start_date
                    end_time = new_end_date
                    #print "\n\n======FINAL DATE",start_time,end_time
                    if start_time < final_date:
                        vals = {
                            'name': self.name,
                            'subject_id' : self.subject_id and self.subject_id.id or False,
                            'intake_id' : self.intake_id and self.intake_id.id or False,
                            'start_time' : new_start_date,
                            'end_time' : new_end_date,
                            'teacher_id' : self.teacher_id and self.teacher_id.id or False,
                            'classroom_id' : self.classroom_id and self.classroom_id.id or False,
                            'recurrenced': True,
                        }
                        self_id = self.create(vals)
                        if self.student_ids:
                            for stud_id in self.student_ids:
                                self.env['ems.class.student.line'].create({
                                    'student_id': stud_id.student_id and stud_id.student_id.id or False,
                                    'is_absent': stud_id.is_absent,
                                    'is_present': stud_id.is_present,
                                    'roll_no': stud_id.roll_no,
                                    'ems_id': self_id and self_id.id or False
                                })
            if end_type == 'count':
                count = self.count
                for i in range(count):
                    new_start_date = start_time + timedelta(days=interval)
                    new_end_date = end_time + timedelta(days=interval)
                    # Exclude Weekend
                    weekday = new_start_date.weekday()
                    if self.exclude_weekend:
                        if weekday == 5:
                            new_start_date = start_time + timedelta(days=interval+2)
                            new_end_date = end_time + timedelta(days=interval+2)
                        if weekday == 6:
                            new_start_date = start_time + timedelta(days=interval+1)
                            new_end_date = end_time + timedelta(days=interval+1)
                    
                    # Exclude Public Holiday
                    if self.exclude_public:
                        #print "\n\n======new_start_date==",new_start_date
                        date_dict = self.exclude_public_holiday(new_start_date,new_end_date,interval)
                        if date_dict.has_key('new_start_date'):
                            #print "\n\n###new_start_date=",date_dict['new_start_date']
                            str_date = date_dict['new_start_date'].strftime('%Y-%m-%d')
                            hr_holiday_lines_objs =  hr_holiday_lines_pool.search([('holiday_date','=',str_date)])
                            if hr_holiday_lines_objs:
                                date_dict = self.exclude_public_holiday(new_start_date,new_end_date,interval)
                                new_start_date = date_dict['new_start_date']
                                new_end_date = date_dict['new_end_date']
                                #print "\n\n===new_start_date=",new_start_date,new_end_date
                            else:
                                new_start_date = date_dict['new_start_date']
                                new_end_date = date_dict['new_end_date']
                                weekday = new_start_date.weekday()
                                if weekday == 5:
                                    new_start_date = new_start_date + timedelta(days=2)
                                    new_end_date = new_end_date + timedelta(days=2)
                                if weekday == 6:
                                    new_start_date = new_start_date + timedelta(days=1)
                                    new_end_date = new_end_date + timedelta(days=1)
                                #print "\n\n******new_start_date=",new_start_date,new_end_date
                                str_date = new_start_date.strftime('%Y-%m-%d')
                                hr_holiday_lines_objs =  hr_holiday_lines_pool.search([('holiday_date','=',str_date)])
                                if hr_holiday_lines_objs:
                                    date_dict = self.exclude_public_holiday(new_start_date,new_end_date,interval)
                                    new_start_date = date_dict['new_start_date']
                                    new_end_date = date_dict['new_end_date']
                    #####
                    start_time = new_start_date
                    end_time = new_end_date
                    vals = {
                        'name': self.name,
                        'subject_id' : self.subject_id and self.subject_id.id or False,
                        'intake_id' : self.intake_id and self.intake_id.id or False,
                        'start_time' : new_start_date,
                        'end_time' : new_end_date,
                        'teacher_id' : self.teacher_id and self.teacher_id.id or False,
                        'classroom_id' : self.classroom_id and self.classroom_id.id or False,
                        'recurrenced': True,
                    }
                    self_id = self.create(vals)
                    if self.student_ids:
                        for stud_id in self.student_ids:
                            self.env['ems.class.student.line'].create({
                                'student_id': stud_id.student_id and stud_id.student_id.id or False,
                                'is_absent': stud_id.is_absent,
                                'is_present': stud_id.is_present,
                                'roll_no': stud_id.roll_no,
                                'ems_id': self_id and self_id.id or False
                            })
            self.write({'recurrenced': True})
        return True

class EmsClassStudentLine(models.Model):
    _name = 'ems.class.student.line'
    
    
    @api.onchange('student_id')
    def _onchange_student_id(self):
        self.update({'roll_no': self.student_id.roll_no})
    
    ems_id = fields.Many2one('ems.class', 'Class')
    student_id = fields.Many2one('student.student', 'Name', required=True)
    roll_no = fields.Integer('Roll No.', required=True, help='Roll Number')
    is_present = fields.Boolean('Present', help="Check if student is present")
    is_absent = fields.Boolean('Absent', help="Check if student is absent")
    
class DailyAttendance(models.Model):
    _inherit = 'daily.attendance'
    
    '''@api.multi
    @api.onchange('standard_id')
    def onchange_standard_id(self):
        return True'''
    
    @api.onchange('class_id')
    def _onchange_class_id(self):
        student_list = []
        
        if self.class_id.student_ids:
            for student in self.class_id.student_ids:
                student_list.append({
                	'roll_no': student.roll_no,
                    'stud_id': student.student_id.id,
                    'is_present': True
                })
        values = {
            'subject_id': self.class_id.subject_id.id,
            'academic_year_id': self.class_id.intake_id.id,
            'date': self.class_id.start_time,
            'teacher_id': self.class_id.teacher_id.id,
            'classroom_id': self.class_id.classroom_id.id,
        }
        self.student_ids = student_list
        self.update(values)
