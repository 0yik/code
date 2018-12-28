import math

from odoo import api, models, fields, tools, _
from datetime import datetime, timedelta
from odoo.tools import amount_to_text_en, float_round
from odoo.exceptions import ValidationError, Warning as UserError


class RegistrationFee(models.Model):
    _inherit = 'class.registration'

    def _get_fees(self):
        for registration_id in self:
            fees_id = self.env['student.fees.register'].search([('class_registration_id', '=', registration_id.id)])
            registration_id.fees_count = len(fees_id)

    fees_count = fields.Integer(string='# of Bills', compute='_get_fees', readonly=True)

    @api.multi
    def action_view_fees(self):
        action = self.env.ref('atts_school_fees.action_student_fees_register_form').read()[0]
        action['domain'] = [('class_registration_id', '=', self.id)]
        return action

    invoice_count = fields.Integer(string='# of Bills', compute='_get_invoice_count', readonly=True)

    def _get_invoice_count(self):
        for registration in self:
            registration.invoice_count = len(self.env['student.fees.invoice'].search([('registration_id', '=', registration.id)]))

    @api.multi
    def action_view_invoice(self):
        action = self.env.ref('atts_school_fees.action_student_fees_invoice').read()[0]
        action['domain'] = [('registration_id', '=', self.id)]
        return action

    def get_invoice_date(self):
        date_start = datetime.strptime(fields.Date.today(), tools.DEFAULT_SERVER_DATE_FORMAT)
        date = date_start.strftime('%d') + '-' + date_start.strftime('%b') + '-' + date_start.strftime('%y')
        return date

    def get_invoice_no(self):
        return self.env['ir.sequence'].next_by_code('fee.invoice')

    def get_course_date(self):
        course_date = ''
        if self.class_id.date_start or self.class_id.date_end:
            if self.class_id.date_start:
                date_start = datetime.strptime(self.class_id.date_start, tools.DEFAULT_SERVER_DATE_FORMAT)
                start_year = date_start.strftime('%Y')
                course_date = date_start.strftime('%d') + ' ' + date_start.strftime('%b') + ' ' + date_start.strftime('%Y')
            if self.class_id.date_end:
                date_end = datetime.strptime(self.class_id.date_end, tools.DEFAULT_SERVER_DATE_FORMAT)
                end_year = date_end.strftime('%Y')
                course_date = date_end.strftime('%d') + ' ' + date_end.strftime('%b') + ' ' + date_end.strftime('%Y')
        if self.class_id.date_start and self.class_id.date_end:
            date_start = datetime.strptime(self.class_id.date_start, tools.DEFAULT_SERVER_DATE_FORMAT)
            date_end = datetime.strptime(self.class_id.date_end, tools.DEFAULT_SERVER_DATE_FORMAT)
            course_date = date_start.strftime('%d') + ' ' + date_start.strftime('%b') + '- ' + date_end.strftime('%d') + ' ' + date_end.strftime('%b') + ' ' + date_end.strftime('%Y')
            if date_start.strftime('%Y') != date_end.strftime('%Y'):
                course_date = date_start.strftime('%d') + ' ' + date_start.strftime('%b') +  ' ' +  date_start.strftime('%Y') + ' - ' + date_end.strftime('%d') + ' ' + date_end.strftime('%b') + ' ' + date_end.strftime('%Y')
        return course_date
        
    def get_course_time(self):
        course_time = ''
        if self.class_id.time_start or self.class_id.time_end:
            if self.class_id.time_start:
                time = '{0:02.0f}:{1:02.0f}'.format(*divmod(self.class_id.time_start * 60, 60))
                d = datetime.strptime(time, "%H:%M")
                course_time = d.strftime("%I:%M %p")
            if self.class_id.time_end:
                time = '{0:02.0f}:{1:02.0f}'.format(*divmod(self.class_id.time_end * 60, 60))
                d = datetime.strptime(time, "%H:%M")
                course_time = d.strftime("%I:%M %p")
        if self.class_id.time_start and self.class_id.time_end:
            start_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(self.class_id.time_start * 60, 60))
            start = datetime.strptime(start_time, "%H:%M")
            end_time = '{0:02.0f}:{1:02.0f}'.format(*divmod(self.class_id.time_end * 60, 60))
            end = datetime.strptime(end_time, "%H:%M")
            course_time = start.strftime("%I:%M %p") + ' to ' + end.strftime("%I:%M %p")
        return course_time

    def get_fee_register(self):
        return self.env['student.fees.register'].search([('name', '=', self.id), ('state', '=', 'confirm')])[0].fees_structure

    def get_amount_in_word(self, amount):
        check_amount_in_words = amount_to_text_en.amount_to_text(math.floor(amount), lang='en', currency='')
        check_amount_in_words = check_amount_in_words.replace(' and Zero Cent', '') # Ugh
        decimals = amount % 1
        if decimals >= 10**-2:
            check_amount_in_words += _(' And Cents %s Only') % str(int(round(float_round(decimals*100, precision_rounding=1))))
        return check_amount_in_words

    def get_start_time(self, start_time):
        return '{0:02.0f}:{1:02.0f}'.format(*divmod(start_time * 60, 60))

    def get_end_time(self, end_time):
        return '{0:02.0f}:{1:02.0f}'.format(*divmod(end_time * 60, 60))

    def get_nationality(self):
        nationality = self.nationality
        if self.nationality == 'singapore_citizen':
            nationality = 'Singapore Citizen'
        if self.nationality == 'singapore_permanent_resident':
            nationality = 'Singapore Permanent Resident'
        if self.nationality == 'others':
            nationality = self.country_id and self.country_id.name
        return nationality

    def create_class_student(self, name, delegate_id=False):
        return {
            'class_id': self.class_id.id,
            'student_id': self.student_id.id,
            'student_name': name,
            'registration_id': self.id,
            'training_date': self.class_id.date_start,
            'delegate_id': delegate_id,
        }

    @api.multi
    def fees_reservation_confirm(self):
        for rec in self:
            ctx = {}
            if not self.email:
                raise ValidationError(_('Kindly, Add Email.'))
            ctx['reservation_email'] = self.email
            try:
                template = self.env.ref('atts_school_fees.email_template_reserve', raise_if_not_found=False)
            except ValueError:
                pass
            if not template:
                template = self.env.ref('atts_school_fees.email_template_reserve')
            ctx['send_email'] = self.env.user.email
            ctx['attachment_ids'] = []
            if self.individual_billing and self.delegate_lines:
                ctx['reservation_email'] = ctx['reservation_email'] + ',' + ','.join([delegate_id.delegate_email for delegate_id in self.delegate_lines if delegate_id.delegate_email])
            ctx['registration_id'] = self
            ctx['company_name'] = self.env.user.company_id.name
            sent_mail = template.with_context(ctx).send_mail(self.id, force_send=True, raise_exception=False)
            if self.registration_type == 'individual':
                self.env['class.student.list'].create(self.create_class_student(self.name))
            else:
                if self.delegate_lines and self.individual_billing:
                    for delegate_id in self.delegate_lines:
                        invoice_id = self.env['student.fees.invoice'].search([('delegate_id', '=', delegate_id.id)], limit=1)
                        if invoice_id and invoice_id.state == 'paid':
                            self.env['class.student.list'].create(self.create_class_student(delegate_id.delegate_name, delegate_id=delegate_id.id))
                else:
                    self.env['class.student.list'].create(self.create_class_student(self.name))
            rec.state = "confirm"
        return True

    # auto check use in cron
    @api.multi
    def process_cancel_reservation(self):
        reservation_ids = self.search([('state' , '=', 'confirm'),
            ('payment_deadline', '=', fields.Date.today()),
            ('registration_type', '=', 'individual')])
        for reservation_id in reservation_ids:
            class_student_ids = self.env['class.student.list'].search([
                ('registration_id', '=', reservation_ids.id),
                ('class_id', '=', reservation_ids.class_id.id)
            ])
            for student_id in class_student_ids:
                student_id.unlink()
            reservation_id.registration_cancel()

    @api.multi
    def process_payment_reminder(self):
        ctx = {}
        ctx['send_email'] = self.env.user.email
        reminder_date = datetime.strptime(fields.Date.today(), tools.DEFAULT_SERVER_DATE_FORMAT) + timedelta(days=7) 
        reservation_ids = self.search([('state' , '=', 'confirm'), ('class_id.date_start', '=', reminder_date)])
        try:
            template = self.env.ref('atts_school_fees.email_template_payment_reminder', raise_if_not_found=False)
        except ValueError:
            pass
        if not template:
            template = self.env.ref('atts_school_fees.email_template_payment_reminder')
        for reservation_id in reservation_ids:
            ctx['reminder_fee_email'] = reservation_id.email
            if reservation_id.individual_billing and reservation_id.delegate_lines:
                ctx['reminder_fee_email'] = ctx['reminder_fee_email'] + ',' + ','.join([delegate_id.delegate_email for delegate_id in reservation_id.delegate_lines if delegate_id.delegate_email]) 
            ctx['company_name'] = self.env.user.company_id.name
            sent_mail = template.with_context(ctx).send_mail(reservation_id.id, force_send=True, raise_exception=False)

    @api.multi
    def class_list_cancel_refund_satelement(self):
        class_student_list_obj = self.env['class.student.list']
        student_fees_invoice_obj = self.env['student.fees.invoice']
        for reservation in self:
            domain = [
                ('registration_id', '=', reservation.id),
                ('class_id', '=', reservation.class_id.id)
            ]
            if reservation.delegate_lines and reservation.individual_billing:
                for delegate in reservation.delegate_lines:
                    for invoice in student_fees_invoice_obj.search([('registration_id', '=', reservation.id), ('delegate_id', '=', delegate.id)]):
                        if invoice.state != 'paid':
                            domain.append(('delegate_id', '=', delegate.id))
                            class_student_list_obj.search(domain).unlink()
            else:
                for invoice in student_fees_invoice_obj.search([('registration_id', '=', reservation.id)]):
                    if invoice.state != 'paid':
                        class_student_list_obj.search(domain).unlink()

    @api.multi
    def registration_cancel(self):
        fees_invoice_obj = self.env['student.fees.invoice']
        for reg in self:
            for inv in fees_invoice_obj.search([('registration_id', '=', reg.id)]):
                if inv.state != 'paid':
                    inv.state = 'cancel'
            reg.state = 'cancel'
        self.class_list_cancel_refund_satelement()


class ClassStudentList(models.Model):
    _inherit = 'class.student.list'

    registration_id = fields.Many2one('class.registration', 'Registration')
    delegate_id = fields.Many2one('registration.delegate.lines', 'Delegate Lines')


class RegistrationDelegateLines(models.Model):
    _inherit = 'registration.delegate.lines'

    def get_nationality(self):
        nationality = self.delegate_nationality
        if self.delegate_nationality == 'singapore_citizen':
            nationality = 'Singapore Citizen'
        if self.delegate_nationality == 'singapore_permanent_resident':
            nationality = 'Singapore Permanent Resident'
        if self.delegate_nationality == 'others':
            nationality = self.country_id and self.country_id.name
        return nationality
 