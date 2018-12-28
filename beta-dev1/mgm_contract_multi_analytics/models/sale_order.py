from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({
            'sale_order_id': self.id,
        })
        return invoice_vals

    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        res = super(SaleOrder, self).action_invoice_create(grouped, final)
        for invoice in res:
            account_invoice = self.env['account.invoice'].search([('id', '=', invoice)])
            account_invoice.write({'sale_order_id': self.id})
        return res


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    @api.multi
    def _create_invoice(self, order, so_line, amount):
        res = super(SaleAdvancePaymentInv, self)._create_invoice(order, so_line, amount)
        for invoice in res:
            sale_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
            invoice.write({'sale_order_id': sale_orders[0].id})
        return res

