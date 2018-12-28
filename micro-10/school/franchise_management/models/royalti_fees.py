# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class royalti_fees(models.Model):
    
    _name = "royalti.fees"
    
    name = fields.Char("Name")
    code = fields.Char("Code")
    type = fields.Selection([('num_student','Number of Student'),('perbill','Per Bill')])
    duration = fields.Selection([('hourly','Hourly'),('monthly','Monthly'),('yearly','Yearly')])
    tax_id = fields.Many2one("account.tax",string="Taxes")
    account_id = fields.Many2one("account.account",string="Account")