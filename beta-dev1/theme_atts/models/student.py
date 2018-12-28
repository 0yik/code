# -*- coding: utf-8 -*-

from odoo import models, fields

class Student(models.Model):
    _inherit = "student.student"

    student_type = fields.Selection([('corporate', 'Corporate'), ('individual', 'Individual')], string="Student Type", related="user_id.partner_id.student_type")

    name = fields.Char('Name')
    nric_passport = fields.Char('NRIC/Passport')
    date_of_birth = fields.Date("Date of Birth")
    email = fields.Char('Email ID')
    nationality = fields.Selection([
        ('singapore_citizen', 'Singapore Citizen'),
        ('singapore_permanent_resident', 'Singapore Permanent Resident'),
        ('others', 'Others'),
    ], string="Nationality")
    country_id = fields.Many2one('res.country', string='Country')
    contact_number = fields.Char('Mobile Number')
    mail_address = fields.Text('Mailing Address')
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
    ], string="Special Dietary Request")
    dietary_request_comment = fields.Char('Dietary Request Comment')
    payment_method = fields.Selection([
        ('cash_payment', 'Cash Payment'),
        ('bank_transfer', 'Bank Transfer'),
        ('local_cheque', 'Local Cheque'),
        ('credit_card', 'Credit Card')
    ], string="Payment Method")

    uen_no_company_number = fields.Char('UEN No/Company Number')
    company_address = fields.Text('Company Address')
    billing_address = fields.Text('Billing Address')
    certi_mailing_add = fields.Text('Certification Mailing Address')
    contact_person = fields.Char('Contact Person')
    fax_no = fields.Char('Fax No')
