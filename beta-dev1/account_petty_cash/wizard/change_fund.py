# -*- coding: utf-8 -*-

from odoo import api, fields, models
from odoo.addons import decimal_precision as dp
from odoo.tools import float_compare, float_is_zero
from odoo.tools.translate import _


class ChangeFundWizard(models.TransientModel):

    _name = 'account.pettycash.fund.change'
    _description = 'Petty Cash Fund Change Wizard'

    @api.model
    def _get_fund(self):

        fund_id = self.env.context.get('active_id', False)
        return fund_id

    @api.model
    def _get_fund_name(self):

        name = False
        fnd = self.env['account.pettycash.fund'].browse(self._get_fund())
        if fnd:
            name = fnd.name
        return name

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
    fund_name = fields.Char(default=_get_fund_name)
    custodian = fields.Many2one('res.users', default=_get_custodian)
    fund_amount = fields.Float(
        related='fund.amount', readonly=True,
        digits=dp.get_precision('Product Price'))
    new_amount = fields.Float(
        digits=dp.get_precision('Product Price'),
        default=_get_fund_amount)
    payable_account = fields.Many2one(
        'account.account', domain=[('user_type_id.type', '=', 'payable')])
    receivable_account = fields.Many2one(
        'account.account', domain=[('user_type_id.type', '=', 'receivable')])
    effective_date = fields.Date(required=True)
    do_receivable = fields.Boolean()
    move = fields.Many2one('account.move', string="Journal Entry")

    @api.onchange('new_amount')
    def onchange_new_amount(self):

        for wiz in self:
            res = False
            if float_compare(wiz.new_amount, wiz.fund_amount,
                             precision_digits=2) == -1:
                res = True
            wiz.do_receivable = res

    @api.multi
    def change_fund(self):

        # Create the petty cash fund
        #
        for wizard in self:
            fnd = wizard.fund

            # Make necessary changes to fund
            #
            update_vals = {}
            if fnd.name and fnd.name != wizard.fund_name:
                update_vals.update({'name': wizard.fund_name})
            if wizard.custodian and fnd.custodian.id != wizard.custodian.id:
                update_vals.update({'custodian': wizard.custodian.id})
            fnd.write(update_vals)

            # Is there is a change in fund amount create journal entries
            #
            if not float_is_zero(wizard.new_amount, precision_digits=2) \
                and float_compare(
                    fnd.amount, wizard.new_amount, precision_digits=2) != 0:

                action = 'Increase'
                if float_compare(wizard.new_amount, fnd.amount,
                                 precision_digits=2) == -1:
                    action = 'Decrease'
                desc = _("%s Petty Cash Fund (%s)"
                         % (action, wizard.fund.name))

                # If it is an increase create a payable account entry. If
                # we are decreasing the fund amount it should be a receivable
                # from the custodian.
                #
                if action == 'Increase':
                    move = fnd.create_payable_journal_entry(
                        fnd, wizard.payable_account.id, wizard.effective_date,
                        wizard.new_amount - wizard.fund_amount, desc)
                else:
                    move = fnd.create_receivable_journal_entry(
                        fnd, wizard.receivable_account.id,
                        wizard.effective_date,
                        wizard.fund_amount - wizard.new_amount, desc)
                wizard.move = move

                # Change the amount on the fund record
                fnd.change_fund_amount(wizard.new_amount)
