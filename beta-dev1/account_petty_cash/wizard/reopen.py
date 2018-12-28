# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.tools import float_compare
from odoo.tools.translate import _


class ReopenFundWizard(models.TransientModel):

    _name = 'account.pettycash.fund.reopen'
    _description = 'Petty Cash Fund Re-open Wizard'

    @api.model
    def _get_fund(self):

        fund_id = self.env.context.get('active_id', False)
        return fund_id

    @api.model
    def _get_fund_amount(self):

        amount = False
        fnd = self.env['account.pettycash.fund'].browse(self._get_fund())
        if fnd:
            amount = fnd.amount
        return amount

    @api.model
    def _get_custodian(self):

        _id = False
        fnd = self.env['account.pettycash.fund'].browse(self._get_fund())
        if fnd:
            _id = fnd.custodian.id
        return _id

    # Fields
    #
    fund = fields.Many2one(
        'account.pettycash.fund', default=_get_fund, required=True)
    fund_amount = fields.Float(
        digits=dp.get_precision('Product Price'), required=True,
        default=_get_fund_amount)
    custodian = fields.Many2one(
        'res.users', required=True, default=_get_custodian)
    payable_account = fields.Many2one('account.account', required=True,
                                      domain=[('user_type_id.type', '=', 'payable')])
    effective_date = fields.Date(required=True)
    payable_move = fields.Many2one('account.move', string="Journal Entry")

    @api.multi
    def reopen_fund(self):

        # Create the petty cash fund
        #
        for wizard in self:
            fnd = wizard.fund

            desc = _("Re-open Petty Cash Fund (%s)" % (wizard.fund.name))

            # Make necessary changes to fund
            #
            update_vals = {}
            if fnd.custodian.id != wizard.custodian.id:
                update_vals.update({'custodian': wizard.custodian.id})
            if float_compare(
                    fnd.amount, wizard.fund_amount, precision_digits=2) != 0:
                update_vals.update({'amount': wizard.fund_amount})
            fnd.reopen_fund()
            fnd.write(update_vals)

            # Create payable account entry and post it
            #
            move = fnd.create_payable_journal_entry(
                fnd, wizard.payable_account.id, wizard.effective_date,
                wizard.fund_amount, desc)
            wizard.payable_move = move
