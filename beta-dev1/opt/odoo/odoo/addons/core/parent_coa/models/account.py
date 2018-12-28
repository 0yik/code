# -*- coding: utf-8 -*-
from odoo import api, fields, models

class AccountAccount(models.Model):
    _inherit = "account.account"

    parent_id = fields.Many2one('account.account', 'Parent Account')

AccountAccount()