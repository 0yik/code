# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountJournal(models.Model):
    _inherit= "account.journal"

    discount_type = fields.Selection([('Amount', 'Amount'), ('Percentage', 'Percentage')], string='Discount Type',)
    discount_value = fields.Float(string='Discount Rate',help='Choose the value of the Discount')