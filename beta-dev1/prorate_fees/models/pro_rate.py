# -*- coding: utf-8 -*-
import time
from datetime import date, datetime
from odoo import fields, models, exceptions, api, _
from odoo.exceptions import UserError
import calendar

class StudentPayslipLine(models.Model):
    '''Student Fees Structure Line'''
    _inherit = 'student.payslip.line'
    
    type = fields.Selection([('month', 'Monthly'),
                             ('year', 'Yearly'),
                             ('range', 'Range'),
                             ('enrollment_fee', 'Enrollment Fee'),
                             ('application_fee', 'Application Fee'),
                             ('others', 'Others')],
                            'Duration', required=True)

class StudentFeesStructureLine(models.Model):
    '''Student Fees Structure Line'''
    _inherit = 'student.fees.structure.line'
    
    pro_rate_fees = fields.Boolean('Pro-Rate Fee')
    type = fields.Selection([('month', 'Monthly'),
                             ('year', 'Yearly'),
                             ('range', 'Range'),
                             ('enrollment_fee', 'Enrollment Fee'),
                             ('application_fee', 'Application Fee'),
                             ('others', 'Others')],
                            'Duration', required=True)

class StudentStudent(models.Model):
    _inherit = 'student.student'
    
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
            # Assign group to student
            rec.user_id.write({'groups_id': [(6, 0, [emp_group.id,student_group.id])], 'active': True})
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
            #Create a student History
            student_history_pool = self.env['student.history']
            history_vals = {
                'academice_year_id': rec.year and rec.year.id or False,
                'standard_id' : rec.standard_id and rec.standard_id.id or False,
                'student_id' : rec and rec.id or False    
            }
            student_history_pool.create(history_vals)
            
            #Create a Draft Fee Receipt for the Enrollment Fees
            student_payslip = self.env['student.payslip']
            payslip_vals = {
                'student_id': self and self.id or False,
                'name': 'Fee Receipt - ' + self.name,
                'date': fields.Date.today(),
                'division_id' : rec.division_id and rec.division_id.id or False,
                'type': 'out_refund',
                'company_id': rec.school_id.company_id and rec.school_id.company_id.id or False,
            }
            if rec.year.enrollment_fee_id:
                payslip_vals.update({'fees_structure_id' : rec.year.enrollment_fee_id and rec.year.enrollment_fee_id.id or False})
            student_payslip_id = student_payslip.create(payslip_vals)
            
            #Create a Draft Fee Receipt for the Pro-Rate Fees
            prorate_payslip_vals = {
                'student_id': self and self.id or False,
                'name': 'Pro Rate Fee Receipt - ' + self.name,
                'date': fields.Date.today(),
                'division_id' : rec.division_id and rec.division_id.id or False,
                'type': 'out_refund',
                'company_id': rec.school_id.company_id and rec.school_id.company_id.id or False,
            }
            if rec.year.enrollment_fee_id:
                prorate_payslip_vals.update({'fees_structure_id' : rec.year.enrollment_fee_id and rec.year.enrollment_fee_id.id or False})
            pro_rated_student_payslip_id = student_payslip.create(prorate_payslip_vals)
            
            student_payslip_line_pool = self.env['student.payslip.line']
            if rec.year.enrollment_fee_id.line_ids:    
                for fee_structure_line in rec.year.enrollment_fee_id.line_ids:
                    #For Enrollment Fee only when you done the student
                    if fee_structure_line.type == 'enrollment_fee':
                        payslip_line_vals = {
                            'name': fee_structure_line.name,
                            'code': fee_structure_line.code,
                            'type': fee_structure_line.type,
                            'account_id' : fee_structure_line.account_id and fee_structure_line.account_id.id or False,
                            'amount': fee_structure_line.amount or 0.00,
                            'slip_id': student_payslip_id and student_payslip_id.id or False
                        }
                        student_payslip_line_pool.create(payslip_line_vals)
                    #For Pro-Rate Fee only when you done the student
                    if fee_structure_line.pro_rate_fees:
                        amount = fee_structure_line.amount
                        ems_class_pool = self.env['ems.class']
                        today_date = datetime.now()
                        start_date = datetime(today_date.year, today_date.month, 1)
                        end_date = datetime(today_date.year, today_date.month, calendar.mdays[today_date.month]).replace(hour=23, minute=59,second=59)
                        receipt_amount = 0
                        total_ems_class = ems_class_pool.search_count([
                    				('intake_id','=',rec.year.id),('end_time','>=',str(start_date)),('start_time','<=',str(end_date))])
                        if total_ems_class:
                            today_last_hours = today_date.replace(hour=00, minute=00,second=00)
                            absent_ems_class = ems_class_pool.search_count([
                    				('intake_id','=',rec.year.id),('end_time','>',str(start_date)),('start_time','<',str(today_last_hours))])
                            per_class_amount = amount / total_ems_class
                            receipt_amount = (total_ems_class - absent_ems_class) * per_class_amount
                        payslip_line_vals = {
                            'name': fee_structure_line.name,
                            'code': fee_structure_line.code,
                            'type': fee_structure_line.type,
                            'account_id' : fee_structure_line.account_id and fee_structure_line.account_id.id or False,
                            'amount': ("%.2f" % receipt_amount) or 0.00,
                            'slip_id': pro_rated_student_payslip_id and pro_rated_student_payslip_id.id or False
                        }
                        student_payslip_line_pool.create(payslip_line_vals)
        return True
