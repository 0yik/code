# -*- coding: utf-8 -*-
import time
from datetime import date, datetime
from odoo import fields, models, exceptions, api, _
from odoo.exceptions import UserError
import calendar

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

class EmsClassStudentLine(models.Model):
    _name = 'ems.class.student.line'
    
    
    roll_no = fields.Integer('Roll No.', required=True, help='Roll Number')
    ems_id = fields.Many2one('ems.class', 'Class')
    student_id = fields.Many2one('student.student', 'Name', required=True)
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
