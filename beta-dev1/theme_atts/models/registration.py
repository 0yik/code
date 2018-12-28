
from odoo import models, fields, api, _


class ATTSClassRegistration(models.Model):
    _name = "class.registration"
    _rec_name = 'registration_id'

    registration_id = fields.Char(string='Registration', required=True, default=lambda self: _('New'))
    class_id = fields.Many2one('class.class', string='Class', required=True)
    student_id = fields.Many2one('student.student', string='Student', required=True)
    name = fields.Char('Name')
    contact_number = fields.Char('Contact Number')
    nric_passport = fields.Char('NRIC/Passport')
    nationality = fields.Selection([
        ('singapore_citizen', 'Singapore Citizen'),
        ('singapore_permanent_resident', 'Singapore Permanent Resident'),
        ('others', 'Others'),
    ], string="Nationality")
    country_id = fields.Many2one('res.country', string='Country')
    date_of_birth = fields.Date("Date of Birth")
    email = fields.Char('Email ID', required=True)
    mail_address = fields.Text('Mailing Address')
    certi_mailing_add = fields.Text('Certification Mailing Address')
    payment_method = fields.Selection([
        ('cash_payment', 'Cash Payment'),
        ('bank_transfer', 'Bank Transfer'),
        ('local_cheque', 'Local Cheque'),
        ('credit_card', 'Credit Card')
    ], string="Payment Method")
    payment_deadline = fields.Date('Payment Deadline')
    individual_billing = fields.Boolean('Individual Billing')
    company_name = fields.Char('Company Name')
    job_title =  fields.Selection([
        ('design_engineer', 'Design Engineer'),
        ('electrical_assistance_engineer', 'Electrical Assistance Engineer'),
        ('electrical_instrumentation_engineer', 'Electrical &amp; Instrumentation Engineer'),
        ('electrical_instrumentation_technician', 'Electrical &amp; Instrumentation Technician'),
        ('mechanical_engineer', 'Mechanical Engineer'),
        ('mechanical_technician', 'Mechanical Technician'),
        ('production_engineer_electrical', 'Production Engineer(Electrical)'),
        ('production_engineer_mechanical', 'Production Engineer(Mechanical)'),
        ('project_engineer', 'Project Engineer'),
        ('sales_engineer', 'Sales Engineer'),
        ('service_engineer', 'Service Engineer'),
        ('senior_engineer', 'Senior / Engineer'),
        ('others', 'Others'),
    ], string="Job Title")
    dietary_request = fields.Selection([
        ('halal_food', 'Halal Food'),
        ('vegetarian_food', 'Vegetarian Food'),
        ('non_halal_food', 'Non-Halal Food'),
        ('others', 'Others')
    ], string="Dietary Request")
    dietary_request_comment = fields.Char('Dietary Request Comment')
    delegate_lines = fields.One2many('registration.delegate.lines', 'registration_id', 'Delegate Details', copy=True)
    registration_type = fields.Selection([
        ('corporate', 'Corporate'),
        ('individual', 'Individual')
    ], string="Registration Type", default="individual")
    state = fields.Selection([
        ('draft', 'Pending'),
        ('register', 'Registered Fee'),
        ('confirm', 'Confirmed'),
        ('cancel', 'Cancelled'),
    ], 'State', readonly=True, default='draft')

    @api.model
    def create(self, vals):
        if vals.get('registration_id', _('New')) == _('New'):
            vals['registration_id'] = self.env['ir.sequence'].next_by_code('course.registration') or _('New')
        return super(ATTSClassRegistration, self).create(vals)

class StudentDelegateLines(models.Model):
    _name = 'registration.delegate.lines'

    registration_id = fields.Many2one('class.registration', 'Registration')
    is_delegate = fields.Boolean('Is Delegate')
    delegate_name = fields.Char('Name')
    delegate_date = fields.Date("Date of Birth")
    delegate_nationality = fields.Selection([
        ('singapore_citizen', 'Singapore Citizen'),
        ('singapore_permanent_resident', 'Singapore Permanent Resident'),
        ('others', 'Others'),
    ], string="Nationality")
    country_id = fields.Many2one('res.country', string='Country')
    delegate_designation = fields.Char('Designation')
    dietary_request = fields.Char('Dietary Request')
    delegate_number = fields.Char('Mobile Number')
    delegate_email = fields.Char('Email ID')
