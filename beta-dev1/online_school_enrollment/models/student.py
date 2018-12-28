# -*- coding: utf-8 -*-
from odoo import models, fields, api	

class StudentStudent(models.Model):
    ''' Defining a student information '''
    _inherit = 'student.student'

    maritual_status = fields.Selection([('unmarried', 'Unmarried'),
                                        ('married', 'Married'),
                                        ('other', 'Others')],
                                       'Marital Status',
                                       states={'done': [('readonly', True)]})

    # @api.multi
    def admission_done(self):
        # for rec in self:
        res = super(StudentStudent, self).admission_done()
        template_id = self.env.ref('online_school_enrollment.student_registration_confirmation_template_id')
        template_id.sudo().email_to = self.email
        template_id.sudo().send_mail(self.id, force_send=True)
        return res

class SchoolStandard(models.Model):
    ''' Defining a student information '''
    _inherit = 'school.standard'
    _order = 'course_name'

    course_name = fields.Char(related="standard_id.name", store=True)

class StudentPayslip(models.Model):
    _inherit = 'student.payslip'

    @api.model
    def create(self, vals):
        res = super(StudentPayslip, self).create(vals)
        if res.student_id and not res.journal_id:
            journal = self.env['account.journal'].sudo().search([('type', '=', 'sale')], limit=1)
            res.journal_id = journal and journal.id or False
        return res
