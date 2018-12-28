# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import UserError


class WarningOnSaleInvoice(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    @api.multi
    def _create_invoice(self, order, so_line, amount):
        total_inv = 0
        for invoices in self.env['account.invoice'].search([('origin','=',order.name),('state','!=','cancel')]):
            total_inv += invoices.amount_total
        total_inv += amount
        if total_inv > order.amount_total:
            raise UserError(_('You are trying to create invoice more than total price'))
        res = super(WarningOnSaleInvoice, self)._create_invoice(order, so_line, amount)
        return res

    @api.onchange('advance_payment_method')
    def onchange_advance_payment_method(self):
        remaining_amount = total_inv = 0
        if self.advance_payment_method == 'percentage' or "fixed":
            order = self.env['sale.order'].browse(self._context.get('active_ids'))[0]
            for invoices in self.env['account.invoice'].search([('origin', '=', order.name), ('state', '!=', 'cancel')]):
                total_inv += invoices.amount_total

            if total_inv < order.amount_total:
                if self.advance_payment_method == 'percentage':
                    remaining_amount = 100 - ((100 * total_inv) / order.amount_total)
                else:
                    remaining_amount = order.amount_total - total_inv
            return {'value': {'amount': remaining_amount}}
        return {}





