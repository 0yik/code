from odoo import fields,models,api,_

class sale_order(models.Model):

    _inherit = 'sale.order'

    @api.multi
    def _get_payment_amount(self):
        self.ensure_one()

        invoice_ids = self.invoice_ids.search(['|',('name','=',self.name),('origin','=',self.name)])

        res = []
        for invoice_id in invoice_ids:
            res.append(invoice_id.residual)
        try:
            return res[-1]
        except:
            return 0.0

    @api.multi
    def _get_shipping_date(self):
        self.ensure_one()

        picking_ids = self.picking_ids.search(['|', ('name', '=', self.name), ('origin', '=', self.name)])

        res = []
        for picking_id in picking_ids:
            res.append(picking_id.min_date)
        try:
            return res[-1]
        except:
            return False

