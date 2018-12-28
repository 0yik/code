# -*- coding: utf-8 -*-

import time
from odoo import api, models, _
from odoo.exceptions import UserError


class ReportGeneralLedger(models.AbstractModel):
    _inherit = 'report.account.report_generalledger'

    def _get_account_move_entry(self, accounts, init_balance, sortby, display_account):
        res = super(ReportGeneralLedger, self)._get_account_move_entry(accounts, init_balance, sortby, display_account)
        for value in res:
            for line in value.get('move_lines'):
                line_obj = self.env['account.move.line'].browse(line.get('lid'))
                line.update({'user_credit': line_obj.user_credit, 'user_debit': line_obj.user_debit})
        return res