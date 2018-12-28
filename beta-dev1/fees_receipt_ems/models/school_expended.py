# -*- coding: utf-8 -*-
import time
from datetime import date, datetime
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.modules import get_module_resource
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, \
    DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import except_orm, Warning as UserError
from openerp.exceptions import ValidationError

class AcademicYear(models.Model):
    _inherit = 'academic.year'
    
    standard_id = fields.Many2one('school.standard', 'Courses', required=1)
    division_id = fields.Many2one('standard.division', 'Division', required=1)
    enrollment_fee_id = fields.Many2one('student.fees.structure','Enrollment Fees Structure')
    code = fields.Char('Code', required=0, help='Code of academic year')
    
    
    @api.multi
    def name_get(self):
        '''Method to display name and code'''
        return [(rec.id, rec.name) for rec in self]
    
    @api.multi
    @api.onchange('standard_id')
    def onchange_standard_id(self):
        for rec in self:
            rec.division_id = rec.standard_id.division_id and rec.standard_id.division_id.id or False
            if rec.standard_id.enrollment_fee_id:
            	print "\n\nrec.standard_id.enrollment_fee_id=",rec.standard_id.enrollment_fee_id
            	rec.enrollment_fee_id = rec.standard_id.enrollment_fee_id and rec.standard_id.enrollment_fee_id.id or False
            else:
                rec.enrollment_fee_id = False
    
    @api.constrains('date_start', 'date_stop')
    def _check_academic_year(self):
        '''Method to check start date should be greater than end date
           also check that dates are not overlapped with existing academic
           year'''
        if (self.date_stop and self.date_start and
                self.date_stop < self.date_start):
            raise UserError(_('Error! The duration of the academic year'
                              'is invalid.'))
        return True
        

class AcademicMonth(models.Model):
    _inherit = 'academic.month'
    
    code = fields.Char('Code', required=0, help='Code of academic year')
    
    @api.constrains('year_id', 'date_start', 'date_stop')
    def _check_year_limit(self):
        '''Method to check year limit'''
        return True


class StudentStudent(models.Model):
    _inherit = 'student.student'
    
    
    @api.constrains('date_of_birth')
    def check_age(self):
        '''Method to check age should be greater than 5'''
        current_dt = datetime.today()
        if self.date_of_birth:
            start = datetime.strptime(self.date_of_birth,
                                      DEFAULT_SERVER_DATE_FORMAT)
            age_calc = ((current_dt - start).days / 365)
            # Check if age less than 5 years
            if age_calc < 15:
                raise ValidationError(_('Age should be greater than 15 years.'))
    
    @api.multi
    def write(self, vals):
        if vals.has_key('year') and vals.get('year'):
            acadamic_year_id = self.env['academic.year'].browse(vals.get('year'))
            exam_result_pool = self.env['exam.result']
            exam_result_ids = exam_result_pool.search([('student_id','=',self.id),('standard_id','=',self.standard_id.id),('state','=','done')])
            
            student_history_pool = self.env['student.history']
            student_history_ids = student_history_pool.search([('student_id','=',self.id),('standard_id','=',self.standard_id.id)])
            student_history_ids.write({'percentage':exam_result_ids.percentage,'result':exam_result_ids.result})
            
            for history_id in self.history_ids:
                if history_id.standard_id.id == acadamic_year_id.standard_id.id:
                    raise UserError(_('%s already passed %s standard.') % (str(self.name),str(history_id.standard_id.standard_id.name)))
                else:
                    if not history_id.result:
                        raise UserError(_('You can not move students without passed %s Course.') % (str(history_id.standard_id.standard_id.name)))
                    else:
                        if history_id.result != 'Pass':
                            raise UserError(_('You can not move students without passed %s Course.') % (str(history_id.standard_id.standard_id.name)))
            history_vals = {
                'academice_year_id': acadamic_year_id and acadamic_year_id.id or False,
                'standard_id' : acadamic_year_id.standard_id and acadamic_year_id.standard_id.id or False,
                'student_id' : self and self.id or False    
            }
            student_history_pool.create(history_vals)
        res = super(StudentStudent, self).write(vals)
        return res
    
    
    @api.model
    def create(self, vals):
        rec = super(StudentStudent, self).create(vals)
        student_payslip = self.env['student.payslip']
        payslip_vals = {
            'student_id': rec and rec.id or False,
            'name': 'Fee Receipt - ' + rec.name,
            'date': fields.Date.today(),
            'division_id' : rec.division_id and rec.division_id.id or False,
            'type': 'out_refund',
            'company_id': rec.school_id.company_id and rec.school_id.company_id.id or False,
        }
#        rec.user_id.write({'active': False})
        if rec.year.enrollment_fee_id:
            payslip_vals.update({'fees_structure_id' : rec.school_id.application_fee_id and rec.school_id.application_fee_id.id or False,})
        student_payslip_id = student_payslip.create(payslip_vals)
        student_payslip_line_pool = self.env['student.payslip.line']
        if rec.school_id.application_fee_id:
            if rec.school_id.application_fee_id.line_ids:
                for fee_structure_line in rec.school_id.application_fee_id.line_ids:
                    if fee_structure_line.type == 'application_fee':
                        payslip_line_vals = {
                            'name': fee_structure_line.name,
                            'code': fee_structure_line.code,
                            'type': fee_structure_line.type,
                            'account_id' : fee_structure_line.account_id and fee_structure_line.account_id.id or False,
                            'amount': fee_structure_line.amount or 0.00,
                            'slip_id': student_payslip_id and student_payslip_id.id or False
                        }
                        student_payslip_line_pool.create(payslip_line_vals) 
        return rec
    
    
    @api.multi
    def admission_done(self):
        '''Method to confirm admission'''
        school_standard_obj = self.env['school.standard']
        ir_sequence = self.env['ir.sequence']
        student_group = self.env.ref('school.group_school_student')
        emp_group = self.env.ref('base.group_user')
        for rec in self:
            #rec.user_id.write({'active': True})
            #print "\n\n======",rec.user_id.active
            if rec.age <= 5:
                raise except_orm(_('Warning'),
                                 _('''The student is not eligible.
                                   Age is not valid.'''))
            domain = [('standard_id', '=', rec.standard_id.id)]
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
            #Create a student History
            student_history_pool = self.env['student.history']
            history_vals = {
                'academice_year_id': rec.year and rec.year.id or False,
                'standard_id' : rec.standard_id and rec.standard_id.id or False,
                'student_id' : rec and rec.id or False    
            
            }
            student_history_pool.create(history_vals)
            
            #Create a Draft Fee Receipt
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
                payslip_vals.update({'fees_structure_id' : rec.year.enrollment_fee_id and rec.year.enrollment_fee_id.id or False,})
            
            student_payslip_id = student_payslip.create(payslip_vals)
            
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
        return True
    
    
    @api.multi
    @api.onchange('school_id')
    def onchange_school_id(self):
        for rec in self:
            if rec.year:
            	rec.standard_id = rec.year.standard_id and rec.year.standard_id.id or False
            	rec.division_id = rec.year.division_id and rec.year.division_id.id or False
            
    @api.multi
    @api.onchange('year')
    def onchange_year(self):
        for rec in self:
            rec.standard_id = rec.year.standard_id and rec.year.standard_id.id or False
            rec.division_id = rec.year.division_id and rec.year.division_id.id or False


class StudentFeesRegister(models.Model):
    _inherit = 'student.fees.register'
    
    intake_id = fields.Many2one('academic.year', 'Intake', required=True)
    
    @api.multi
    def fees_register_confirm(self):
        '''Method to confirm payslip'''
        student_pool = self.env['student.student']
        payslip_pool = self.env['student.payslip']
        free_structure_pool = self.env['student.fees.structure']
        for rec in self:
            student_ids = student_pool.search([('year','=',rec.intake_id.id)])
            if student_ids:
                for student_id in student_ids:
                    payslip_vals = {
                        'student_id': student_id and student_id.id or False,
                        'name': 'Monthly Fee Receipt - ' + student_id.name,
                        'date': fields.Date.today(),
                        'standard_id' : rec.standard_id and rec.standard_id.id or False,
                        'division_id' : rec.intake_id.division_id and rec.intake_id.division_id.id or False,
                        'type': 'out_refund',
                        'company_id': rec.company_id and rec.company_id.id or False,
                        'register_id': rec and rec.id or False
                    }
                    if rec.fees_structure:
                        payslip_vals.update({'fees_structure_id' : rec.fees_structure and rec.fees_structure.id or False,})
                    student_payslip_id = payslip_pool.create(payslip_vals)
                    student_payslip_line_pool = self.env['student.payslip.line']
                    if rec.fees_structure.line_ids:    
                        for fee_structure_line in rec.fees_structure.line_ids:
                            if fee_structure_line.type == 'month':
                                payslip_line_vals = {
                                    'name': fee_structure_line.name,
                                    'code': fee_structure_line.code,
                                    'type': fee_structure_line.type,
                                    'account_id' : fee_structure_line.account_id and fee_structure_line.account_id.id or False,
                                    'amount': fee_structure_line.amount or 0.00,
                                    'slip_id': student_payslip_id and student_payslip_id.id or False
                                }
                                student_payslip_line_pool.create(payslip_line_vals)
            if not rec.journal_id:
                raise ValidationError(_('Kindly, Select Account Journal'))
            if not rec.fees_structure:
                raise ValidationError(_('Kindly, Select Fees Structure'))
            # Calculate the amount
            amount = 0
            for data in rec.line_ids:
                amount += data.total
            rec.write({'total_amount': amount,
                       'state': 'confirm'})
        return True
    
    
    @api.multi
    @api.onchange('intake_id')
    def onchange_intake_id(self):
        for rec in self:
            rec.standard_id = rec.intake_id.standard_id.standard_id and rec.intake_id.standard_id.standard_id.id or False
            rec.fees_structure = rec.intake_id.enrollment_fee_id and rec.intake_id.enrollment_fee_id.id or False
    
class DailyAttendance(models.Model):
    _inherit = 'daily.attendance'
    
    remarks = fields.Text('Remarks')
    academic_year_id = fields.Many2one('academic.year','Intake')
    
    
    @api.multi
    @api.onchange('academic_year_id')
    def onchange_academic_year_id(self):
        '''Method to get student roll no'''
        stud_list = []
        stud_obj = self.env['student.student']
        for rec in self:
            if rec.academic_year_id:
                rec.standard_id = rec.academic_year_id.standard_id and rec.academic_year_id.standard_id.id or False
                stud_list = [{'roll_no': stu.roll_no, 'name': stu.name}
                             for stu in stud_obj.search([('standard_id', '=',rec.academic_year_id.standard_id.id),
                                                         ('state', '=','done')])]
            rec.attendance_ids = stud_list
    
class StudentPayslip(models.Model):
    _inherit = 'student.payslip'
    
    _sql_constraints = [('code_uniq', 'unique(student_id,date,state,name,number)',
                         'Student Payslip must be unique !')]
    
    @api.one
    @api.depends('line_ids')
    def _compute_amount(self):
        if self.line_ids:
            self.total = sum(line.amount for line in self.line_ids)
        else:
            self.total = 0
    
    total = fields.Float("Total", readonly=True,help="Total Amount",compute='_compute_amount',)
    
    
    @api.onchange('student_id')
    def onchange_student(self):
        '''Method to get standard , division , medium of student selected'''
        if self.student_id:
            self.standard_id = self.student_id.standard_id.standard_id and self.student_id.standard_id.standard_id.id or False
            self.division_id = self.student_id.division_id
            self.medium_id = self.student_id.medium_id
    
    @api.model
    def create(self, vals):
        if vals.get('student_id'):
            student = self.env['student.student'].browse(vals.get('student_id'))
            vals.update({
                'standard_id': student.standard_id.standard_id and student.standard_id.standard_id.id or False,
                'division_id': student.division_id.id,
                'medium_id': student.medium_id.id})
        payslip_id = super(StudentPayslip, self).create(vals)
        return payslip_id
    
    @api.multi
    def write(self, vals):
        if vals.get('student_id'):
            student = self.env['student.student'].browse(vals.get('student_id')
                                                         )
            vals.update({'standard_id': student.standard_id.standard_id and student.standard_id.standard_id.id or False,
                         'division_id': student.division_id.id,
                         'medium_id': student.medium_id.id})
        return super(StudentPayslip, self).write(vals)
    
    @api.multi
    def payslip_confirm(self):
        '''Generate invoice of student fee'''
        for rec in self:
            if not rec.journal_id:
                raise ValidationError(_('Kindly, Select Account Journal'))
            if not rec.fees_structure_id:
                raise ValidationError(_('Kindly, Select Fees Structure'))
            rec.write({'state': 'pending','due_amount':rec.total})
            partner = rec.student_id and rec.student_id.partner_id
            vals = {'partner_id': partner.id,
                    'date_invoice': rec.date,
                    'account_id': partner.property_account_receivable_id and partner.property_account_receivable_id.id or False,
                    'journal_id': rec.journal_id and rec.journal_id.id or False,
                    'slip_ref': rec.number,
                    'student_payslip_id': rec and rec.id or False,
                    'type': 'out_invoice'}
            invoice_line = []
            for line in rec.line_ids:
                acc_id = ''
                if line.account_id.id:
                    acc_id = line.account_id.id
                else:
                    # check type of invoice
                    if rec.type in ('out_invoice', 'in_refund'):
                        acc_id = rec.journal_id.default_credit_account_id and rec.journal_id.default_credit_account_id.id or False
                    else:
                        acc_id = rec.journal_id.default_debit_account_id and rec.journal_id.default_debit_account_id.id or False
                invoice_line_vals = {'name': line.name,
                                     'account_id': acc_id,
                                     'quantity': 1.000,
                                     'price_unit': line.amount}
                invoice_line.append((0, 0, invoice_line_vals))
            vals.update({'invoice_line_ids': invoice_line})
            # creates invoice
            account_invoice_id = self.env['account.invoice'].create(vals)
            account_invoice_id.action_invoice_open()
            invoice_obj = self.env.ref('account.invoice_form')
            return {'name': _("Pay Fees"),
                    'view_mode': 'form',
                    'view_type': 'form',
                    'res_model': 'account.invoice',
                    'view_id': invoice_obj.id,
                    'type': 'ir.actions.act_window',
                    'nodestroy': True,
                    'target': 'current',
                    'res_id': account_invoice_id.id,
                    'context': {}}

class DailyAttendanceLine(models.Model):
    _inherit = 'daily.attendance.line'
    
    remarks = fields.Text('Remarks')
    
class SchoolStandard(models.Model):
    _inherit = 'school.standard'
    
    medium_id = fields.Many2one('standard.medium', 'Medium', required=False)
    enrollment_fee_id = fields.Many2one('student.fees.structure','Enrollment Fee Structure')

class SchoolSchool(models.Model):
    _inherit = 'school.school'
    
    @api.model
    def _lang_get(self):
        '''Method to get language'''
        languages = self.env['res.lang'].search([])
        return [(language.code, language.name) for language in languages]
    
    
    @api.model
    def _get_default_lang(self):
        languages = self.env['res.lang'].search([('code','=','en_US')])
        if languages:
            return languages.code
        else:
            return False
    
    application_fee_id = fields.Many2one('student.fees.structure','Application Fee Structure')
    code = fields.Char('Code', required=0)
    lang = fields.Selection(_lang_get, 'Language', default=_get_default_lang,
                            help='''If the selected language is loaded in the
                                system, all documents related to this partner
                                will be printed in this language.
                                If not, it will be English.''')
    
class MoveCourses(models.Model):
    _name = 'move.courses'
    
    @api.multi
    @api.onchange('course_id')
    def onchange_course_id(self):
        elrolled_student_list = []
        student_pool = self.env['student.student']
        for rec in self:
            student_ids = student_pool.search([('standard_id','=',rec.course_id.id),('state','=','done')])
            if student_ids:
                for student in student_ids:
                    elrolled_student_list.append({
                        'student_id': student and student.id or False,
                        'roll_no': student.roll_no,
                        'checklist': True,
                    })
            rec.enrolled_student_ids = elrolled_student_list
            
    
    name = fields.Char('Name',required=True)
    date = fields.Datetime('Moved On',default=fields.Datetime.now)
    user_id = fields.Many2one('res.users','Moved By',default=lambda self: self.env.user)
    course_id = fields.Many2one('school.standard','Course')
    enrolled_student_ids = fields.One2many('enrolled.student','move_course_id','Enrolled Student')
    
class EnrolledStudent(models.Model):
    _name = 'enrolled.student'
    
    student_id = fields.Many2one('student.student','Student',required=1)
    roll_no = fields.Integer('Roll No')
    checklist = fields.Boolean('Checklist')
    move_course_id = fields.Many2one('move.courses','Move Cousers',readonly=1)


class StudentPayslipLine(models.Model):
    '''Student Fees Structure Line'''
    _inherit = 'student.payslip.line'
    
    amount = fields.Float('Amount', digits=(16, 2))
    code = fields.Char('Code', required=0)
    type = fields.Selection([('month', 'Monthly'),
                             ('year', 'Yearly'),
                             ('range', 'Range'),
                             ('enrollment_fee', 'Enrollment Fee'),
                             ('application_fee', 'Application Fee')],
                            'Duration', required=True)


class StudentFeesStructure(models.Model):
    '''Fees structure'''
    _inherit = 'student.fees.structure'

    code = fields.Char('Code', required=0)

class StudentFeesStructureLine(models.Model):
    '''Student Fees Structure Line'''
    _inherit = 'student.fees.structure.line'
    
    amount = fields.Float('Amount', digits=(16, 2))
    type = fields.Selection([('month', 'Monthly'),
                             ('year', 'Yearly'),
                             ('range', 'Range'),
                             ('enrollment_fee', 'Enrollment Fee'),
                             ('application_fee', 'Application Fee')],
                            'Duration', required=True)

class BatchExamResult(models.TransientModel):
    '''designed for printing batch report'''

    _inherit = "exam.batchwise.result"
    
    @api.multi
    @api.onchange('year')
    def onchange_year(self):
        '''Method to get student roll no'''
        for rec in self:
            rec.standard_id = rec.year.standard_id and rec.year.standard_id.id or False


class MonthlyAttendanceSheet(models.TransientModel):
    _inherit = "monthly.attendance.sheet"
    
    @api.multi
    @api.onchange('year_id')
    def onchange_year_id(self):
        for rec in self:
            rec.standard_id = rec.year_id.standard_id and rec.year_id.standard_id.id or False

class TimeTable(models.Model):
    _inherit = 'time.table'
    
    @api.multi
    @api.onchange('year_id')
    def onchange_year_id(self):
        for rec in self:
            rec.standard_id = rec.year_id.standard_id and rec.year_id.standard_id.id or False
            
class StandardDivision(models.Model):
    ''' Defining a division(A, B, C) related to standard'''
    _inherit = "standard.division"

    code = fields.Char('Code', required=0)
