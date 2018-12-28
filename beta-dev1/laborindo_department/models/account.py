# -*- coding: utf-8 -*-
from odoo import api, fields, models

class AccountAccount(models.Model):
    _inherit = "account.account"

    department_ids = fields.Many2many('res.department', string='Departments')


class account_voucher(models.Model):
    _inherit = 'account.voucher'

    department_id = fields.Many2one('res.department', string='Department')
    project = fields.Char(string='Project')


