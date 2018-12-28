from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import UserError, ValidationError

class ExamExam(models.Model):
    _inherit = 'exam.exam'
    
    student_ids = fields.One2many('exam.student.line', 'exam_id','Students')
    make_up_exam = fields.Boolean('Make Up Exam',default=True)
    make_up_exam_type = fields.Selection([('Regular','Regular'),('Make-Up','Make-Up')],string="Exam Type", default='Regular')
    
    @api.multi
    @api.onchange('academic_year')
    def onchange_academic_year(self):
        student_obj = self.env['student.student']
        student_list = []
        for rec in self:
            if rec.academic_year:
                student_ids = student_obj.search([('year', '=',rec.academic_year.id),('state', '=', 'done')])
                for student in student_ids:
                    student_list.append({
                    	'roll_no': student.roll_no,
                        'student_id': student.id,
                        'standard_id': student.standard_id and student.standard_id.id or False,
                        'is_present': True
                    })
            rec.student_ids = student_list
    
class ExamClassStudentLine(models.Model):
    _name = 'exam.student.line'
    
    @api.onchange('is_present')
    def onchange_is_present(self):
        for rec in self:
            if self.is_present:
                rec.is_absent = False
            else:
                rec.is_absent = True
    
    @api.onchange('is_absent')
    def onchange_is_absent(self):
        for rec in self:
            if self.is_absent:
                rec.is_present = False
            else:
                rec.is_present = True
    
    
    exam_id = fields.Many2one('exam.exam', 'Exam')
    roll_no = fields.Integer('Roll No.', required=True, help='Roll Number')
    student_id = fields.Many2one('student.student', 'Name', required=True)
    standard_id = fields.Many2one('school.standard','Course')
    is_present = fields.Boolean('Present', help="Check if student is present")
    is_absent = fields.Boolean('Absent', help="Check if student is absent")
