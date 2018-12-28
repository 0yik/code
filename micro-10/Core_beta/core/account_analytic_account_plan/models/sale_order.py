# -*- coding: utf-8 -*-

from odoo import models, fields, api

class sale_order_line(models.Model):
    _inherit = 'sale.order.line'

    analytic_distribution_id = fields.Many2one('account.analytic.distribution', string='Analytic Distribution')

    @api.multi
    def _prepare_invoice_line(self, qty):
        res = super(sale_order_line, self)._prepare_invoice_line(qty)
        if self.analytic_distribution_id and self.analytic_distribution_id.id:
            res['analytic_distribution_id'] = self.analytic_distribution_id.id
        return res

    @api.multi
    def create_analytic(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.analytic.distribution',
            'view_type': 'form',
            'view_mode': 'form',
            'res_id': self.analytic_distribution_id.id,
            'target': 'new',
        }
class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.multi
    def _create_invoice(self, order, so_line, amount):
        res = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
        if res and res.id:
            for line in res.invoice_line_ids:
                if line.sale_line_ids:
                    for sale_line in line.sale_line_ids:
                        if sale_line.analytic_distribution_id and sale_line.analytic_distribution_id.id:
                            line.analytic_distribution_id = sale_line.analytic_distribution_id.id
        return res
