# -*- coding: utf-8 -*-

from odoo import api, fields, models


class CloseFundWizard(models.TransientModel):

    _name = 'account.pettycash.fund.close'
    _description = 'Petty Cash Fund Closing Wizard'

    @api.model
    def _get_fund(self):

        fund_id = self.env.context.get('active_id', False)
        return fund_id

    # Fields
    #
    fund = fields.Many2one(
        'account.pettycash.fund', default=_get_fund, required=True)
    receivable_account = fields.Many2one(
        'account.account', domain=[('user_type_id.type', '=', 'receivable')])
    effective_date = fields.Date(required=True)

    @api.multi
    def close_fund(self):

        # Create the petty cash fund
        #
        for wizard in self:
            wizard.fund.close_fund(
                wizard.effective_date, wizard.receivable_account)
