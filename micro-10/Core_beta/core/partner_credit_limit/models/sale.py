# -*- coding: utf-8 -*-
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import api, models, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.one
    def check_limit(self):
        partner = self.partner_id
        # moveline_obj = self.env['account.move.line']
        # movelines = moveline_obj.\
        #     search([('partner_id', '=', partner.id),
        #             ('account_id.user_type_id.name', 'in',
        #             ['Receivable', 'Payable']),
        #             ('full_reconcile_id', '=', False)])
        #
        # debit, credit = 0.0, 0.0
        today_dt = datetime.strftime(datetime.now(), DF)
        # for line in movelines:
        #     if line.date_maturity < today_dt:
        #         credit += line.debit
        #         debit += line.credit

        sale_order_obj = self.env['sale.order']
        sale_orders = sale_order_obj.search([
            ('id', '<', self.id),
            ('partner_id.id', '=', partner.id),
            # ('invoice_status', '=', 'invoiced'),
            ('state', '=', 'sale'),
            ('confirmation_date', '<=',datetime.strftime(datetime.now(),DEFAULT_SERVER_DATETIME_FORMAT))
        ])
        total_amount = 0
        for sale in sale_orders:
            if not sale.invoice_ids:
                total_amount +=sale.amount_total
            else:
                for inv in sale.invoice_ids:
                    if inv.state == 'draft':
                        total_amount += inv.amount_total
                    if inv.state == 'open':
                        total_amount += inv.residual

        # if (credit - debit + self.amount_total) > partner.credit_limit:
        if total_amount + self.amount_total > partner.credit_limit:
            if not partner.over_credit:
                msg = 'Can not confirm Sale Order,Total mature due Amount ' \
                      '%s as on %s !\nCheck Partner Accounts or Credit ' \
                      'Limits !' % (total_amount, today_dt)
                raise UserError(_('Credit Over Limits !\n' + msg))
            else:
                partner.write({
                    'credit_limit': total_amount + self.amount_total})
                return True
        else:
            return True

    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            order.check_limit()
        return res
