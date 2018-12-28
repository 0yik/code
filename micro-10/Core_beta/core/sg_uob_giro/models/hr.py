# -*- coding: utf-8 -*-
from odoo import api, fields, models

class Employee(models.Model):
    _inherit = "hr.employee"

    hr_bank_account_id = fields.Many2one('hr.bank.details', string='Bank Account Number', help='Employee bank salary account', groups='hr.group_hr_user')

Employee()

class HrBankDetails(models.Model):
    _inherit = 'hr.bank.details'

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            res.append((record.id, '%s (%s)' % (record.bank_name, record.bank_ac_no)))
        return res

HrBankDetails()