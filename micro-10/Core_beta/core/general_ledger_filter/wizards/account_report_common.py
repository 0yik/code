# -*- coding: utf-8 -*-
from odoo import api, fields, models

class AccountReportGeneralLedger(models.TransientModel):
    _inherit = 'account.report.general.ledger'

    account_ids = fields.Many2many('account.account', string='Accounts')

AccountReportGeneralLedger()