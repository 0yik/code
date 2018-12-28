# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT

class SubjectGrades(models.Model):
    _name = 'subject.grades'
    _rec_name = 'subject_id'
    
    @api.depends('score_line')
    def _compute_final_result(self):
        for rec in self:
            total = 0
            obtained = 0
            for line in rec.score_line:
                if line.scores:
                    score = line.scores.split(' / ')
                    total += int(score[1])
                    obtained += int(score[0])
            if obtained and total:
                rec.final_result = (obtained * 100) / total
    
    @api.depends('final_result', 'subject_id')
    def _compute_final_grade(self):
        for rec in self:
            if rec.final_result:
                for grade in rec.subject_id.grade_id.grade_ids:
                    if rec.final_result >= grade.from_mark and rec.final_result <= grade.to_mark:
                        rec.final_grade = grade.grade

    student_id = fields.Many2one("student.student", string="Student")
    subject_id = fields.Many2one("subject.subject", string="Subject")
    term_id = fields.Many2one("academic.month", string="Term")
    score_line = fields.One2many("breakdown.scores", "grade_id", string="Breakdowns")
    final_result = fields.Integer("Final Result", compute='_compute_final_result', store=True)
    final_grade = fields.Char("Final Grade", compute='_compute_final_grade', store=True)
    
    @api.onchange('student_id', 'subject_id', 'term_id')
    def onchange_subject(self):
        score_line = []
        if self.student_id and self.subject_id and self.term_id:
            attendance_present_ids = self.env['daily.attendance.line'].search([('stud_id', '=', self.student_id.id), ('standard_id.subject_id', '=', self.subject_id.id), ('standard_id.subject_id.term_id', '=', self.term_id.id), ('is_present', '=', True)])
            attendance_total_ids = self.env['daily.attendance.line'].search([('stud_id', '=', self.student_id.id), ('standard_id.subject_id', '=', self.subject_id.id), ('standard_id.subject_id.term_id', '=', self.term_id.id)])
            present = len(attendance_present_ids)
            total = len(attendance_total_ids)
            if present and total:
                point = (present * 100) / total
            else:
                point = 0
            for breakdown in self.subject_id.breakdown_line:
                if breakdown.description == 'Attendance':
                    score = '0'
                    if point:
                        score = int((point * breakdown.weightage) / breakdown.subject_id.maximum_marks)
                        score_line.append({'breakdowns': breakdown.description,
                                           'scores': str(score) + ' / ' + str((int(breakdown.weightage) * int(breakdown.subject_id.maximum_marks)) / 100)
                                         })
            exam_result_ids = self.env['exam.subject'].search([('exam_id.student_id', '=', self.student_id.id), ('subject_id', '=', self.subject_id.id), ('subject_id.term_id', '=', self.term_id.id),('exam_id.state', '=', 'done')])
            for breakdown in self.subject_id.breakdown_line:
                if breakdown.description == 'Exam':
                    score = '0'
                    if exam_result_ids and exam_result_ids[0].obtain_marks:
                        score = int((exam_result_ids[0].obtain_marks * breakdown.weightage) / breakdown.subject_id.maximum_marks)
                        score_line.append({'breakdowns': breakdown.description,
                                               'scores': str(score) + ' / ' + str((int(breakdown.weightage) * int(breakdown.subject_id.maximum_marks)) / 100)
                                             })
            assignment_ids = self.env['student.assignment'].search([('student_id', '=', self.student_id.id),('assignment_id.subject_id', '=', self.subject_id.id),('assignment_id.subject_id.term_id', '=', self.term_id.id),('state', '=', 'evaluated')])
            for breakdown in self.subject_id.breakdown_line:
                if breakdown.description == 'Assignment':
                    score = '0'
                    if assignment_ids and assignment_ids[0].marks:
                        score = int((assignment_ids[0].marks * breakdown.weightage) / breakdown.subject_id.maximum_marks)
                        score_line.append({'breakdowns': breakdown.description,
                                         'scores': str(score) + ' / ' + str((int(breakdown.weightage) * int(breakdown.subject_id.maximum_marks)) / 100)
                                         })
        self.score_line = score_line

    @api.multi
    def action_subject_grades(self):
        student_ids = self.env['student.student'].search([])
        for student in student_ids:
            attendance_present_ids = self.env['daily.attendance.line'].search([('stud_id', '=', student.id), ('is_present', '=', True)])
            attendance_total_ids = self.env['daily.attendance.line'].search([('stud_id', '=', student.id)])
            present = len(attendance_present_ids)
            total = len(attendance_total_ids)
            if present and total:
                point = (present * 100) / total
            else:
                point = 0
            subject = attendance_total_ids[0].standard_id.subject_id if len(attendance_total_ids) > 0 else False
            subject_id = attendance_total_ids[0].standard_id.subject_id.id if len(attendance_total_ids) > 0 else False
            term = attendance_total_ids[0].standard_id.subject_id.term_id.id if len(attendance_total_ids) > 0 else False
            grade_ids = self.env['subject.grades'].search([('student_id', '=', student.id), ('subject_id', '=', subject_id), ('term_id', '=', term)])
            if grade_ids:
                grade_id = grade_ids[0]
            else:
                grade_id = self.env['subject.grades'].create({'student_id': student.id,
                                               'subject_id': subject_id,
                                               'term_id': term,
                                             })
            if subject:
                for breakdown in subject.breakdown_line:
                    if breakdown.description == 'Attendance':
                        score = '0'
                        if point:
                            score = int((point * breakdown.weightage) / breakdown.subject_id.maximum_marks)
                        score_id = self.env['breakdown.scores'].search([('grade_id', '=', grade_id.id), ('breakdowns', '=', breakdown.description)])
                        if score_id:
                            score_id.write({'grade_id': grade_id.id,
                                                             'breakdowns': breakdown.description,
                                                             'scores': str(score) + ' / ' + str(int(breakdown.weightage) * int(breakdown.subject_id.maximum_marks) / 100)
                                                             })
                        else:
                            self.env['breakdown.scores'].create({'grade_id': grade_id.id,
                                                             'breakdowns': breakdown.description,
                                                             'scores': str(score) + ' / ' + str(int(breakdown.weightage) * int(breakdown.subject_id.maximum_marks) / 100)
                                                             })
                            
        exam_result_ids = self.env['exam.result'].search([('state', '=', 'done')])
        for exam in exam_result_ids:
            for line in exam.result_ids:
                grade_ids = self.env['subject.grades'].search([('student_id', '=', line.exam_id.student_id.id), ('subject_id', '=', line.subject_id.id), ('term_id', '=', line.subject_id.term_id.id)])
                if grade_ids:
                    grade_id = grade_ids[0]
                else:
                    grade_id = self.env['subject.grades'].create({'student_id': line.exam_id.student_id.id,
                                                   'subject_id': line.subject_id.id,
                                                   'term_id': line.subject_id.term_id.id,
                                                 })
                for breakdown in line.subject_id.breakdown_line:
                    if breakdown.description == 'Exam':
                        score = '0'
                        if line.obtain_marks:
                            score = int((line.obtain_marks * breakdown.weightage) / breakdown.subject_id.maximum_marks)
                        score_id = self.env['breakdown.scores'].search([('grade_id', '=', grade_id.id), ('breakdowns', '=', breakdown.description)])
                        if score_id:
                            score_id.write({'grade_id': grade_id.id,
                                             'breakdowns': breakdown.description,
                                             'scores': str(score) + ' / ' + str(int(breakdown.weightage) * int(breakdown.subject_id.maximum_marks) / 100)
                                             })
                        else:
                            self.env['breakdown.scores'].create({'grade_id': grade_id.id,
                                                             'breakdowns': breakdown.description,
                                                             'scores': str(score) + ' / ' + str(int(breakdown.weightage) * int(breakdown.subject_id.maximum_marks) / 100)
                                                             })
        
        assignment_ids = self.env['student.assignment'].search([('state', '=', 'evaluated')])
        for assignment in assignment_ids:
            grade_ids = self.env['subject.grades'].search([('student_id', '=', assignment.student_id.id), ('subject_id', '=', assignment.assignment_id.subject_id.id), ('term_id', '=', assignment.assignment_id.subject_id.term_id.id)])
            if grade_ids:
                grade_id = grade_ids[0]
            else:
                grade_id = self.env['subject.grades'].create({'student_id': assignment.student_id.id,
                                               'subject_id': assignment.assignment_id.subject_id.id,
                                               'term_id': assignment.assignment_id.subject_id.term_id.id,
                                             })
            for breakdown in assignment.assignment_id.subject_id.breakdown_line:
                if breakdown.description == 'Assignment':
                    score = '0'
                    if assignment.marks:
                        score = int((assignment.marks * breakdown.weightage) / breakdown.subject_id.maximum_marks)
                    score_id = self.env['breakdown.scores'].search([('grade_id', '=', grade_id.id), ('breakdowns', '=', breakdown.description)])
                    if score_id:
                        score_id.write({'grade_id': grade_id.id,
                                                         'breakdowns': breakdown.description,
                                                         'scores': str(score) + ' / ' + str(int(breakdown.weightage) * int(breakdown.subject_id.maximum_marks) / 100)
                                                         })
                    else:
                        self.env['breakdown.scores'].create({'grade_id': grade_id.id,
                                                         'breakdowns': breakdown.description,
                                                         'scores': str(score) + ' / ' + str(int(breakdown.weightage) * int(breakdown.subject_id.maximum_marks) / 100)
                                                         })

class BreakdownScores(models.Model):
    _name = 'breakdown.scores'
    
    grade_id = fields.Many2one("subject.grades", string="Grade")
    breakdowns = fields.Char("Breakdowns")
    scores = fields.Char("Scores")
    
    
class OverallGPA(models.Model):
    _name = 'overall.gpa'
    _rec_name = 'student_id'
    
    @api.depends('gpa_line')
    def _compute_gpa_term(self):
        for rec in self:
            point_list = []
            for line in rec.gpa_line:
                grade = line.grade
                for grade_line in line.subject_id.grade_id.grade_ids:
                    if grade == grade_line.grade:
                        point_dict = {'weightage' : float(line.subject_id.weightage),
                                      'grade_point': float(grade_line.grade_point)
                                      }
                        point_list.append(point_dict)
            up_count = 0.0
            down_count = 0.0
            for point in point_list:
                up_count += point.get('grade_point') * point.get('weightage')
                down_count += point.get('weightage')
            if up_count and down_count and up_count > 0.0 and down_count > 0.0:
                rec.gpa_term = str(up_count / down_count)
                rec.cumulative_gpa = str(up_count / down_count)

    student_id = fields.Many2one("student.student", string="Student")
    term_id = fields.Many2one("academic.month", string="Term")
    gpa_line = fields.One2many("gpa.line", "gpa_id", string="GPA")
    gpa_term = fields.Char("GPA of the Term", compute='_compute_gpa_term', store=True)
    cumulative_gpa = fields.Char("Cumulative GPA", compute='_compute_gpa_term', store=True)
    
    @api.multi
    def action_overall_gpa(self):
        student_ids = self.env['student.student'].search([])
        term_ids = self.env['academic.month'].search([])
        for student in student_ids:
            for term in term_ids:
                grade_ids = self.env['subject.grades'].search([('student_id', '=', student.id), ('term_id', '=', term.id)])
                if grade_ids:
                    gpa_ids = self.env['overall.gpa'].search([('student_id', '=', student.id), ('term_id', '=', term.id)])
                    if gpa_ids:
                        gpa_id = gpa_ids[0]
                    else:
                        gpa_id = self.env['overall.gpa'].create({'student_id': student.id,
                                                                 'term_id': term.id
                                                                 })
                    for grade in grade_ids:
                        line_id = self.env['gpa.line'].search([('gpa_id', '=', gpa_id.id), ('subject_id', '=', grade.subject_id.id)])
                        if line_id:
                            line_id.write({'gpa_id': gpa_id.id,
                                                     'subject_id': grade.subject_id.id,
                                                     'grade': grade.final_grade
                                                     })
                        else:
                            self.env['gpa.line'].create({'gpa_id': gpa_id.id,
                                                     'subject_id': grade.subject_id.id,
                                                     'grade': grade.final_grade
                                                     })
        
class GPALine(models.Model):
    _name = 'gpa.line'
    
    gpa_id = fields.Many2one("overall.gpa", string="GPA")
    subject_id = fields.Many2one("subject.subject", string="Subject")
    grade = fields.Char(string="Grade")
    
class ClassAssignment(models.Model):
    _inherit = 'class.assignment'
    _rec_name = 'title'
    
    subject_id = fields.Many2one("subject.subject", string="Subject")
    title = fields.Many2one('breakdown.weightage','Title')


class StudentAssignment(models.Model):
    _inherit = 'student.assignment'
    _rec_name = 'title'
    
    @api.one
    @api.depends('assignment_id', 'assignment_id.name', 'assignment_id.title', 'assignment_id.date_due', 'assignment_id.class_id',
        'assignment_id.attachment')
    def _get_assignment_details(self):
        self.name = self.assignment_id.name
        self.title = self.assignment_id.title and self.assignment_id.title.id or False
        self.description = self.assignment_id.description
        self.date_due = self.assignment_id.date_due
        self.class_id = self.assignment_id.class_id.id
        self.created_user_id = self.assignment_id.created_user_id.id
        self.created_date = self.assignment_id.created_date
        self.attachment = self.assignment_id.attachment
        self.file_name = self.assignment_id.file_name
    
    title = fields.Many2one('breakdown.weightage','Title',compute=_get_assignment_details, store=True)
   
