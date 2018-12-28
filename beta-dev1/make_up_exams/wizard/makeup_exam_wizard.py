# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from openerp.tools.translate import _
from datetime import datetime,tzinfo,timedelta
import time


class makeup_exam_wizard(models.TransientModel):
    _name = 'makeup.exam.wizard'
    
    start_date = fields.Datetime('Start Date', required=True)
    end_date = fields.Datetime('End Date', required=True)
    
    
    @api.multi
    def make_up_exam(self):
        exam_pool = self.env['exam.exam']
        exam_obj = exam_pool.browse(self._context.get('active_id'))
        exam_obj.write({'make_up_exam': False})
        exam_student_line_id_list = []
        if exam_obj.student_ids:
            for student_line in exam_obj.student_ids:
                if student_line.is_absent:
                    student_line_vals = {
                        'student_id': student_line.student_id and student_line.student_id.id or False,
                        'roll_no': student_line.student_id.roll_no,
                        'is_present': True,
                        'is_absent': False,
                        'standard_id': student_line.standard_id and student_line.standard_id.id or False,
                    }
                    exam_student_line_id = self.env['exam.student.line'].create(student_line_vals)
                    exam_student_line_id_list.append(exam_student_line_id.id)
        standard_id_list = []
        if exam_obj.standard_id:
            for standard_id in exam_obj.standard_id:
                standard_id_list.append(standard_id.id)
        exam_vals = {
            'subject_id':exam_obj.subject_id and exam_obj.subject_id.id or False,
            'name': exam_obj.name and exam_obj.name.id or False,
            'grade_system': exam_obj.grade_system and exam_obj.grade_system.id or False,
            'academic_year': exam_obj.academic_year and exam_obj.academic_year.id or False,
            'start_date': self.start_date or False,
            'end_date': self.end_date or False,
            'state': 'draft',
            'student_ids': [( 6, 0, exam_student_line_id_list)],
            'standard_id': [( 6, 0, standard_id_list)],
            'make_up_exam': True,
            'make_up_exam_type':'Make-Up',
        }
        exam_id = exam_pool.create(exam_vals)
        return True
    
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
