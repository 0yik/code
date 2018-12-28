# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
class Employee(models.Model):

    _inherit = "hr.employee"
    # we need a related field in order to be able to sort the employee by name
    birthday = fields.Date('Date of Birth', groups="base.group_user")
    ssnid = fields.Char('SSN No', help='Social Security Number', groups="base.group_user")
    sinid = fields.Char('SIN No', help='Social Insurance Number', groups="base.group_user")
    identification_id = fields.Char(string='Identification No', groups="base.group_user")
    gender = fields.Selection([
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], groups="base.group_user")
    marital = fields.Selection([
        ('single', 'Single'),
        ('married', 'Married'),
        ('widower', 'Widower'),
        ('divorced', 'Divorced')
    ], string='Marital Status', groups="base.group_user")
    bank_account_id = fields.Many2one('res.partner.bank', string='Bank Account Number',
        domain="[('partner_id', '=', address_home_id)]", help='Employee bank salary account', groups="base.group_user")
    passport_id = fields.Char('Passport No', groups="base.group_user")
