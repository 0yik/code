from odoo import fields,models,api,_

class sale_order(models.Model):

    _inherit = 'stock.picking'

    @api.multi
    def _get_stock_payment_amount(self):
        self.ensure_one()
        invoice = self.env['account.invoice']
        invoice_ids = invoice.search(['|',('name','=',self.origin),('origin','=',self.origin)])

        res = []
        for invoice_id in invoice_ids:
            res.append(invoice_id.residual)
        try:
            return res[-1]
        except:
            return 0.0

    @api.multi
    def _get_stock_text_amount(self):
        self.ensure_one()
        sale_order = self.env['sale.order']
        sale_ids = sale_order.search(['|', ('name', '=', self.origin), ('origin', '=', self.origin)])

        res = []
        for sale_id in sale_ids:
            res.append(sale_id.amount_tax)
        try:
            return res[-1]
        except:
            return 0.0


    @api.multi
    def _get_delivery_price_amount(self):
        self.ensure_one()
        sale_order = self.env['sale.order']
        sale_ids = sale_order.search(['|', ('name', '=', self.name), ('origin', '=', self.name)])

        res = []
        for sale_id in sale_ids:
            res.append(sale_id.delivery_price)
        try:
            return res[-1]
        except:
            return 0.0

    @api.multi
    def _get_delivery_date_due(self):
        self.ensure_one()
        invoice = self.env['account.invoice']
        invoice_ids = invoice.search(['|', ('name', '=', self.origin), ('origin', '=', self.origin)])

        res = []
        for invoice_id in invoice_ids:
            res.append(invoice_id.date_due)
        try:
            return res[-1]
        except:
            return False

    @api.multi
    def _get_invoice_date(self):
        self.ensure_one()
        invoice = self.env['account.invoice']
        invoice_ids = invoice.search(['|', ('name', '=', self.origin), ('origin', '=', self.origin)])

        res = []
        for invoice_id in invoice_ids:
            res.append(invoice_id.create_date)
        try:
            return res[-1]
        except:
            return False
