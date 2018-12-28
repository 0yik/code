# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.float_utils import float_compare
from odoo.exceptions import UserError

class account_journal(models.Model):
    _inherit="account.journal"

    cash_account = fields.Many2one('account.account', string="Cash Account", domain=lambda self: [('user_type_id.id', '=', self.env.ref('account.data_account_type_liquidity').id)])

account_journal()