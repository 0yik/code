# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.

import time
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, Warning as UserError
from datetime import datetime


class StudentFeesRegister(models.Model):
    '''Student fees Register'''
    _name = 'student.fees.register'
    _description = 'Student fees Register'
    _rec_name = 'number'


    class_registration_id = fields.Many2one('class.registration', 'Registration')
    date = fields.Date('Date', required=True,
                       help="Date of register",
                       default=lambda * a: time.strftime('%Y-%m-%d'))
    number = fields.Char('Number', readonly=True,
                         default=lambda obj: obj.env['ir.sequence'].
                         next_by_code('student.fees.register'))
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm')],
                            'State', readonly=True, default='draft')
    register_lines = fields.One2many('student.fees.register.line', 'register_id', 'Fees Register')
    registration_type = fields.Selection(related='class_registration_id.registration_type', string="Registration Type")
    payment_deadline = fields.Date(related='class_registration_id.class_id.date_start')
    invoice_count = fields.Integer(string='# of Bills', compute='_get_invoice_count', readonly=True)
    payment_term_id = fields.Many2one('account.payment.term', string='Payment Terms')
    remarks = fields.Text(string='Remarks')

    def _get_invoice_count(self):
        for registration in self:
            registration.invoice_count = len(self.env['student.fees.invoice'].search([('fee_registration_id', '=', registration.id)]))

    @api.multi
    def action_view_invoice(self):
        action = self.env.ref('atts_school_fees.action_student_fees_invoice').read()[0]
        action['domain'] = [('fee_registration_id', '=', self.id)]
        return action

    @api.multi
    def fees_register_draft(self):
        '''Changes the state to draft'''
        for rec in self:
            rec.state = 'draft'
        return True

    def invoice_send(self, invoice_id):
        ctx = {}
        ctx['send_email'] = self.env.user.email
        template = self.env.ref('atts_school_fees.email_template_reservation_invoice')
        ctx['student_email'] = invoice_id.student_email
        ctx['company_name'] = self.env.user.company_id.name
        sent_mail = template.with_context(ctx).send_mail(invoice_id.id, force_send=True, raise_exception=False)

    @api.multi
    def fees_register_confirm(self):
        for rec in self:
            fees_invoice_obj = self.env['student.fees.invoice']
            invoice_lines = []
            for line in rec.register_lines:
                invoice_lines.append((0, 0, {
                        'fee_head_id': line.fee_head_id.id,
                        'details': line.details,
                        'amount': line.amount,
                        'quantity': line.quantity,
                        'tax': line.tax,
                        'total': line.total,
                    }))
            values = {
                'registration_id': rec.class_registration_id.id,
                'fee_registration_id': rec.id,
                'date': rec.date,
                'payment_term_id': rec.payment_term_id.id,
                'invoice_lines': invoice_lines,
            }
            if rec.class_registration_id.registration_type == 'corporate' and rec.class_registration_id.individual_billing:
                for line in rec.class_registration_id.delegate_lines:
                    values.update({'name': 'New', 'student_name':line.delegate_name, 'student_email': line.delegate_email, 'delegate_id': line.id})
                    invoice_id = fees_invoice_obj.create(values)
                    self.invoice_send(invoice_id)
            else:
                values.update({'name': 'New', 'student_name':rec.class_registration_id.name, 'student_email': rec.class_registration_id.email})
                invoice_id = fees_invoice_obj.create(values)
                self.invoice_send(invoice_id)
            rec.state = "confirm"
            if rec.class_registration_id.state == 'draft':
                rec.class_registration_id.state = 'register'
        return True

    @api.multi
    def validate_fees(self):
        for rec in self:
            rec.class_registration_id.state = 'register'
        return True

    @api.model
    def create(self, values):
        """ Override to avoid automatic logging of creation """
        ctx = {}
        register_id = super(StudentFeesRegister, self).create(values)
        if register_id:
            # self._cr.execute('update register_student_list set name=%s where register_id=%s',(register_id.date,register_id.id));
            ctx['send_email'] = self.env.user.company_id.email
            email_list = [user.email for user in self.env['res.users'].search([]) if user.has_group('atts_course.group_marketing_manager')]
            ctx['marketing_managers'] = ','.join([email for email in email_list if email])
            base_url = self.env['ir.config_parameter'].get_param('web.base.url')
            db = self.env.cr.dbname
            ctx['action_url']  = "{}/web?db={}#id={}&view_type=form&model=student.fees.register".format(base_url, db, register_id.id)
            template = self.env.ref('atts_school_fees.email_template_fee_register')
            ctx['company_name'] = self.env.user.company_id.name
            sent_mail = template.with_context(ctx).send_mail(register_id.id, force_send=True, raise_exception=False)
        return register_id

class StudentFeesRegisterLine(models.Model):
    '''Student Fees Structure Line'''
    _name = 'student.fees.register.line'
    _description = 'Student Fees Register Line'

    @api.onchange('fee_head_id')
    def _on_fee_head_id(self):
        for line in self:
            line.details = line.fee_head_id.name
            line.amount = line.fee_head_id.amount
            line.quantity = (line.register_id.class_registration_id.registration_type == 'corporate' and not line.register_id.class_registration_id.individual_billing) and len(line.register_id.class_registration_id.delegate_lines) or 1
            line.tax = line.fee_head_id.gst
            line.total = (line.amount * line.quantity) * (1 + line.tax/100)

    @api.depends('amount', 'quantity', 'tax')
    def _compute_amount(self):
        for line in self:
            line.total = (line.amount * line.quantity) * (1 + line.tax/100)

    register_id = fields.Many2one('student.fees.register', 'Register')
    fee_head_id = fields.Many2one('student.fees.structure.line', string='Description')
    details = fields.Char('Details')
    amount = fields.Float('Amount', digits=(16, 2))
    quantity = fields.Integer('Quantity', default=1)
    tax = fields.Float('TAX(%)', digits=(16, 2), default=7)
    total = fields.Float(compute='_compute_amount', string='Total', readonly=True, store=True)

class RegisterStudentList(models.Model):
    '''Register Student List'''
    _name = 'register.student.list'
    _description = 'Student List'

    name = fields.Date('Name')
    fee_head_id = fields.Many2one('student.fees.structure.line',string='Fee Head')
    register_id = fields.Many2one('student.fees.register', 'Register')
    student_id = fields.Many2one('student.student','Student')
    class_no = fields.Char('Class')
    total = fields.Float('Total', digits=(16, 2))
    amount_paid = fields.Float('Amount Paid', digits=(16, 2))
    status = fields.Selection([('fully_paid', 'Fully Paid'),
                             ('pending', 'pending')],
                            'Status')
    @api.onchange('student_id')
    def onchange_student(self):
        '''Method to get standard , division , medium of student selected'''
        if self.student_id:
            self.class_no = self.student_id.class_level + self.student_id.class_number
    @api.onchange('fee_head_id')
    def onchange_fee_head_id(self):
        '''Method to get standard , division , medium of student selected'''
        if self.fee_head_id:
            self.total = self.fee_head_id.amount


class StudentPayslip(models.Model):
    _name = 'student.payslip'
    _description = 'Student PaySlip'

    name = fields.Many2one('class.registration', 'Registration', required="1")
    date = fields.Date('Date', readonly=True,
                       help="Current Date of payslip",
                       default=lambda * a: time.strftime('%Y-%m-%d'))
    amount = fields.Float('Amount', digits=(16, 2), required="1")

    @api.model
    def create(self, vals):
        res = super(StudentPayslip, self).create(vals)
        res.name.state = 'paid'
        return res


class StudentPayslipLine(models.Model):
    '''Student PaySlip Line'''
    _name = 'student.payslip.line'
    _description = 'Student PaySlip Line'

    name = fields.Char('Name')
    fee_head_id = fields.Many2one('student.fees.structure.line',string='Fee Head')
    code = fields.Char('Code', required=True)
    amount = fields.Float('Amount', digits=(16, 2))
    amount_paid = fields.Float('Amount Paid', digits=(16, 2))
    slip_id = fields.Many2one('student.payslip', 'Pay Slip')
    description = fields.Text('Description')
    start_date = fields.Date('Start Date')
    end_date = fields.Date('End Date')
    
class StudentFeesStructure(models.Model):
    '''Fees structure'''
    _name = 'student.fees.structure'
    _description = 'Student Fees Structure'

    @api.multi
    @api.depends('line_ids')
    def _total_amount(self):
        '''Method to compute total amount'''
        for rec in self:
            total_amt = 0.0
            for line in rec.line_ids:
                total_amt += line.subtotal
            rec.total = total_amt

    name = fields.Char('Name', required=True)
    total = fields.Float("Total", compute="_total_amount", store=True)
    line_ids = fields.Many2many('student.fees.structure.line',
                                'fees_structure_payslip_rel',
                                'fees_id', 'slip_id', 'Fees Structure')


class StudentFeesStructureLine(models.Model):
    '''Student Fees Structure Line'''
    _name = 'student.fees.structure.line'
    _description = 'Student Fees Structure Line'
    _order = 'sequence'

    @api.depends('gst', 'amount')
    def _total_amount(self):
        for rec in self:
            rec.subtotal = rec.amount
            if rec.gst and rec.amount:
                if rec.amount < 0:
                    rec.subtotal = (rec.amount * rec.gst) / 100
                else:
                    rec.subtotal = rec.amount + ((rec.amount * rec.gst) / 100)

    name = fields.Char('Name', required=True)
    gst = fields.Float('GST(%)', digits=(16, 2), default=7)
    amount = fields.Float('Amount', digits=(16, 2))
    subtotal = fields.Float('Subtotal', digits=(16, 2), compute="_total_amount")
    sequence = fields.Integer('Sequence')
    is_course_head = fields.Boolean('Is Course Head', default=False)
    
class StudentStudent(models.Model):
    ''' Defining a student information '''
    _inherit = 'student.student'
    _description = 'Student Information'
    
    email_address = fields.Char('Email Address')
    
    @api.multi
    def print_billing(self):
        return self.env['report'].get_action([], 'school_fees.billing_report')
    