# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api
from odoo.tools.translate import _

class MoveCoursesWizard(models.TransientModel):
    _name = 'move.courses.wizard'

    school_id = fields.Many2one('school.school', 'School',required=True)
    standard_id = fields.Many2one('school.standard', 'Courses',required=True)
    academic_year_id = fields.Many2one('academic.year', 'Intake',required=True)
    moved = fields.Boolean('Moved')
    message = fields.Text('Message')

    @api.multi
    def move_courses(self):
        '''Code for moving student to next standard'''
        
        student_history_pool = self.env['student.history']
        move_courses_obj = self.env['move.courses'].browse(self._context['active_id'])
        for enrolled_student_id in move_courses_obj.enrolled_student_ids:
            student_id = enrolled_student_id.student_id
            if enrolled_student_id.checklist:
                student_payslip = self.env['student.payslip']
                payslip_vals = {
                    'student_id': student_id and student_id.id or False,
                    'name': 'Fee Receipt - ' + student_id.name,
                    'date': fields.Date.today(),
                    'standard_id' : student_id.standard_id.standard_id and student_id.standard_id.standard_id.id or False,
                    'division_id' : student_id.division_id and student_id.division_id.id or False,
                    'type': 'out_refund',
                    'company_id': student_id.school_id.company_id and student_id.school_id.company_id.id or False,
                }
                if student_id.year.enrollment_fee_id:
                    enrollment_fee_id = self.academic_year_id.enrollment_fee_id
                    payslip_vals.update({'fees_structure_id' : enrollment_fee_id and enrollment_fee_id.id or False})
                
                print "\n\npayslip_vals=",payslip_vals
                student_payslip_id = student_payslip.create(payslip_vals)
                student_payslip_line_pool = self.env['student.payslip.line']
                print "\n\n&&&&&&77self.academic_year_id.enrollment_fee_id.line_ids",self.academic_year_id.enrollment_fee_id.line_ids
                if self.academic_year_id.enrollment_fee_id.line_ids:    
                    for fee_structure_line in self.academic_year_id.enrollment_fee_id.line_ids:
                        if fee_structure_line.type == 'enrollment_fee':
		                    payslip_line_vals = {
		                        'name': fee_structure_line.name,
		                        'code': fee_structure_line.code,
		                        'type': fee_structure_line.type,
		                        'account_id' : fee_structure_line.account_id and fee_structure_line.account_id.id or False,
		                        'amount': fee_structure_line.amount or 0.00,
		                        'slip_id': student_payslip_id and student_payslip_id.id or False
		                    }
		                    print "\n\nenrollment_fee=",payslip_line_vals
		                    student_payslip_line_pool.create(payslip_line_vals)
                print "\n\n===self.school_id==",student_id.school_id,self.school_id
                if student_id.school_id != self.school_id:
		            if self.school_id.application_fee_id.line_ids:    
		                for fee_structure_line in self.school_id.application_fee_id.line_ids:
		                    if fee_structure_line.type == 'application_fee':
				                print "\n\n***********application_fee"
				                payslip_line_vals = {
				                    'name': fee_structure_line.name,
				                    'code': fee_structure_line.code,
				                    'type': fee_structure_line.type,
				                    'account_id' : fee_structure_line.account_id and fee_structure_line.account_id.id or False,
				                    'amount': fee_structure_line.amount or 0.00,
				                    'slip_id': student_payslip_id and student_payslip_id.id or False
				                }
				                print "\n\napplication_fee=",payslip_line_vals
				                student_payslip_line_pool.create(payslip_line_vals)
                student_id.write({
                    'year': self.academic_year_id and self.academic_year_id.id or False,
                    'standard_id': self.standard_id and self.standard_id.id or False,
                    'school_id': self.school_id and self.school_id.id or False,
                })
        message = _('All students moved from %s TO %s.') % (str(move_courses_obj.course_id.standard_id.name),str(self.academic_year_id.standard_id.standard_id.name))
        self.write({
        	'moved': True,
        	'message': message,
        })
        
        return {"type": "ir.actions.do_nothing"}
