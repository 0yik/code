# -*- coding: utf-8 -*-
import time
from datetime import datetime
from odoo import fields, models, exceptions, api, _
from odoo.exceptions import UserError

class ResPartner(models.Model):
    '''Defining a address information '''
    _inherit = 'res.partner'
    _description = 'Address Information'

    @api.model
    def create(self, vals):
        '''Method creates parents assign group parents'''
        res = super(ResPartner, self).create(vals)
        res_user_pool = self.env['res.users']
        res_user_id = res_user_pool.search([('partner_id','=',res.id)])
        if res_user_id:
            res_user_id.unlink()
        return res
        
class StudentStudent(models.Model):
    _inherit = 'student.student'
    
    
    @api.model
    def create(self, vals):
        rec = super(StudentStudent, self).create(vals)
        rec.user_id.write({'active': False})
        return rec
    
    
    @api.multi
    def admission_done(self):
        '''Method to confirm admission'''
        school_standard_obj = self.env['school.standard']
        ir_sequence = self.env['ir.sequence']
        student_group = self.env.ref('school.group_school_student')
        emp_group = self.env.ref('base.group_user')
        for rec in self:
            if rec.age <= 5:
                raise except_orm(_('Warning'),
                                 _('''The student is not eligible.
                                   Age is not valid.'''))
            domain = [('standard_id', '=', rec.standard_id.id)]
            # Checks the standard if not defined raise error
            if not school_standard_obj.search(domain):
                raise except_orm(_('Warning'),
                                 _('''The courses is not defined in a
                                     school'''))
            # Assign group to student
            rec.user_id.write({'groups_id': [(6, 0, [emp_group.id,student_group.id])],'active': True})
            # Assign roll no to student
            number = 1
            for rec_std in rec.search(domain):
                rec_std.roll_no = number
                number += 1
            # Assign registration code to student
            reg_code = ir_sequence.next_by_code('student.registration')
            reg_code_str = ''
            if rec.school_id.state_id:
                reg_code_str += str(rec.school_id.state_id.name)
            if rec.school_id.city:
                reg_code_str += '/' + str(rec.school_id.city)
            if rec.school_id.name:
                reg_code_str += '/' + str(rec.school_id.name)
            if reg_code:
                reg_code_str += '/' + str(rec.school_id.name)
            #registation_code = (str(rec.school_id.state_id.name) + str('/') +
            #                    str(rec.school_id.city) + str('/') +
            #                    str(rec.school_id.name) + str('/') +
            #                    str(reg_code))
            stu_code = ir_sequence.next_by_code('student.code')
            student_code = (str(rec.school_id.code) + str('/') +
                            str(rec.year.code) + str('/') +
                            str(stu_code))
            rec.write({'state': 'done',
                       'admission_date': time.strftime('%Y-%m-%d'),
                       'student_code': student_code,
                       'reg_code': reg_code_str})
        return True
