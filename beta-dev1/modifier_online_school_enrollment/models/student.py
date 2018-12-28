# -*- coding: utf-8 -*-
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

class EducationBackground(models.Model):
    _name = 'education.background'

    institution = fields.Char('Institution')
    achievement = fields.Text('Achievement')
    from_date = fields.Date('From Date')
    to_date = fields.Date('To Date')
    student_id = fields.Many2one('student.student', 'Student')

class HighestQualification(models.Model):
    _name = 'highest.qualification'

    name = fields.Char('Name')

    _sql_constraints = [
        ('code_name_uniq', 'unique (name)', 'The name must be unique!')
    ]

class GeneralSurvey(models.Model):
    _name = 'general.survey'

    name = fields.Char('Name')

    _sql_constraints = [
        ('code_name_uniq', 'unique (name)', 'The name must be unique!')
    ]   

class StudentStudent(models.Model):
    ''' Defining a student information '''
    _inherit = 'student.student'

    citizenship = fields.Char('Citizenship')
    nric = fields.Char('NRIC', required=True)
    hp_no = fields.Char('Hp No.')
    occupation = fields.Char('Occupation')
    income = fields.Selection([
        ('less_then_1500', 'Less 1500'),
        ('1500_2000', '1500-2000'),
        ('2001_3000', '2001-3000'),
        ('3001_above', '3001 Above'),
        ],string='Income', default='less_then_1500')
    highest_qualification_id = fields.Many2one('highest.qualification', 'Highest Qualification')
    general_survey_id = fields.Many2one('general.survey', 'General Survey')
    education_background_id = fields.One2many('education.background', 'student_id', String='General Survey')

class StudentPayslip(models.Model):
    _inherit = 'student.payslip'

    nric = fields.Char(related="student_id.nric")

    @api.multi
    def get_payslip_id(self):
        invoice_id = self.env['account.invoice'].search([('slip_ref','=',self.number),('student_payslip_id','=',self.id)])
        return invoice_id

class ResUsers(models.Model):
    _inherit = 'res.users'

    @api.multi
    def action_reset_password(self):
        """ create signup token for each user, and send their signup url by email """
        # prepare reset password signup
        create_mode = bool(self.env.context.get('create_user'))

        # no time limit for initial invitation, only for reset password
        expiration = False if create_mode else now(days=+1)

        self.mapped('partner_id').signup_prepare(signup_type="reset", expiration=expiration)

        # send email to users with their signup url
        template = False
        if create_mode:
            try:
                template = self.env.ref('auth_signup.set_password_email', raise_if_not_found=False)
            except ValueError:
                pass
        if not template:
            template = self.env.ref('auth_signup.reset_password_email')
        assert template._name == 'mail.template'

        for user in self:
            if not user.email:
                raise UserError(_("Cannot send email: user %s has no email address.") % user.name)
            if user.active:
                template.with_context(lang=user.lang).send_mail(user.id, force_send=True, raise_exception=True)
                _logger.info("Password reset email sent for user <%s> to <%s>", user.login, user.email)

