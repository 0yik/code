# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
#import webcolors
from odoo.exceptions import UserError, ValidationError

class GradeLine(models.Model):
    _inherit = 'grade.line'
    
    grade_point = fields.Char("Grade Point")
    
class ExamExam(models.Model):
    _inherit = 'exam.exam'
    
    start_date = fields.Datetime("Exam Start Datetime", help="Exam will start from this datetime")
    end_date = fields.Datetime("Exam End Datetime", help="Exam will end at this datetime")
    subject_id = fields.Many2one("subject.subject","Subject", required=True)
    name = fields.Many2one('breakdown.weightage','Exam Name',required=True)
    
    @api.multi
    def set_running(self):
        '''Method to set state to running'''
        for rec in self:
            if not rec.standard_id:
                raise ValidationError(_('Please Select Standard Id.'))
            rec.state = 'running'
        return True
    
class ExamResult(models.Model):
    _inherit = 'exam.result'
    
    @api.onchange('subject_id','minimum_marks','maximum_marks')
    def onchange_subject_id(self):
        for rec in self:
            rec.minimum_marks = float(self.subject_id.minimum_marks)
            rec.maximum_marks = float(self.subject_id.maximum_marks)
    
    
    @api.multi
    @api.depends('obtain_marks','marks_reeval')
    def _compute_total(self):
        '''Method to compute total'''
        for rec in self:
            if rec.marks_reeval > -1:
                rec.total = rec.marks_reeval
                rec.marks_reeval_date = datetime.now()
            else:    
                rec.total = rec.obtain_marks
            
    
    @api.multi
    @api.depends('obtain_marks','minimum_marks','marks_reeval')
    def _compute_result(self):
        '''Method to compute result'''
        for rec in self:
            total_marks = 0.00
            if rec.marks_reeval > -1.00:
                total_marks = rec.marks_reeval
                rec.marks_reeval_date = datetime.now()
            else:
                total_marks = rec.obtain_marks
            if total_marks >= rec.minimum_marks:
                rec.result = 'Pass'
            else:
                rec.result = 'Fail'
    
    
    @api.multi
    @api.depends('total','obtain_marks','minimum_marks','maximum_marks','grade_line_id','marks_reeval')
    def _compute_per(self):
        '''Method to compute percentage'''
        for rec in self:
            percentage = 0
            total_marks = 0.00
            if rec.marks_reeval > -1.00:
                total_marks = rec.marks_reeval
                rec.marks_reeval_date = datetime.now()
            else:
                total_marks = rec.obtain_marks
            if rec.maximum_marks > 0:
                percentage = ((total_marks * 100) / rec.maximum_marks)
            rec.percentage = percentage
            rec.grade = rec.grade_line_id.grade
        return True
    
    
    @api.multi
    @api.depends('obtain_marks','marks_reeval')
    def _compute_grade(self):
        '''Method to compute grade after re-evaluation'''
        for rec in self:
            grade_lines = rec.grade_system.grade_ids
            total_marks = 0.0
            if rec.marks_reeval > -1.00:
                total_marks = rec.marks_reeval
                rec.marks_reeval_date = datetime.now()
            else:
                total_marks = rec.obtain_marks
            if (rec.student_id and grade_lines):
                for grade_id in grade_lines:
                    if total_marks:
                        b_id = total_marks <= grade_id.to_mark
                        if (total_marks >= grade_id.from_mark and b_id):
                            rec.grade_line_id = grade_id
    
    subject_id = fields.Many2one("subject.subject", "Subject", required=True)
    obtain_marks = fields.Float("Obtained Marks")
    minimum_marks = fields.Float("Minimum Marks",help="Minimum Marks of subject")
    maximum_marks = fields.Float("Maximum Marks",help="Maximum Marks of subject")
    marks_reeval = fields.Float("Marks After Re-evaluation",help="Marks Obtain after Re-evaluation", default=-1.00)
    grade_line_id = fields.Many2one('grade.line', "Grade",compute='_compute_grade')
    marks_reeval_date = fields.Datetime("Re-evaluation Date")

'''class SubjectBreakdownDesc(models.Model):
    _name = 'subject.breakdown.desc'
    _rec_name = 'description'
    
    subject_id = fields.Many2one("subject.subject", "Subject")
    description = fields.Char('Description')
    breakdown_type = fields.Selection([('Exam', 'Exam'), ('Assignment', 'Assignment'),('Attendance', 'Attendance')],"Type")'''
 

