# -*- coding: utf-8 -*-

from odoo import models, fields, api

class res_partner(models.Model):
    _inherit = 'res.partner'

    completely = fields.Boolean(string='Completely')
    sms        = fields.Boolean(string='SMS')
    fax        = fields.Boolean(string='Fax')
    call       = fields.Boolean(string='Call')
    no_form    = fields.Boolean(string='No Form')
    preferred_customer = fields.Char(string='Preferred Customer:')
    name_company = fields.Char(string='Company Name:')
    name_employer = fields.Char(string='Employer Name:')
    contract_person = fields.Char(string='Contact Person:')
    contract_hom =fields.Char(string='Contact No.(Home):')
    office = fields.Char(string='Office:')
    contract_mobile = fields.Char(string='Contact No.(Mobile):')
    email = fields.Char('Email')
    nature_of_busines = fields.Char('Nature Of Busines:')
    address = fields.Char('Address:')
    postal_code = fields.Char('Postal Code:')
    chinese_new_year = fields.Boolean(string='Chinese New Year:')
    hari_raya        = fields.Boolean(string='Hari Raya:')
    chrismas         = fields.Boolean(string='Chrismas:')
    nric_passport_ros = fields.Char(string='NIRC/Passport/ROS No:')
    nationality  = fields.Many2one('res.country', string='Nationality:')
    date_birth   = fields.Date(string='Date of Birth:')
    age = fields.Integer()
    gender = fields.Selection([('male','Male'),('female','Female'),('other','Other')],string='Gender:')
    marital_status = fields.Selection([('marital','Married'),('unmarital','Unmarried')],string='Marital Status:')
    occupation = fields.Char(string='Occupation:')
    lic_part_date = fields.Date(string='Lic Part Date:')
    experience    = fields.Integer(string='Experience:')
    notes = fields.Text(string='Notes:')
    previous_name = fields.Char(string='Previous Name:')
    salutation = fields.Char('Salutation')
    # customer_name=fields.Many2one('res.partner', string="Customer Name:")