from odoo import api, fields, models, _

# class product(models.Model):
#     _inherit = 'product.template'
#
#     def _get_default_uom_id(self):
#         return self.env["product.uom"].search([], limit=1, order='id').id
#
#     uom_receive_id = fields.Many2one(
#         'product.uom', 'Receiving Unit of Measure',
#         default=_get_default_uom_id, required=True,
#         help="Default Unit of Measure used for stock picking.")


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'

    @api.model
    def create(self, vals):
        # product = self.env['product.product'].browse(vals['product_id'])
        # uom = self.env['product.uom'].browse(vals['product_uom_id'])
        # vals['product_uom_id'] = product.product_tmpl_id.uom_po_id.id
        # vals['product_qty'] = product.product_tmpl_id.uom_po_id._compute_quantity(vals['product_qty'], uom)
        res = super(StockPackOperation, self).create(vals)
        return res