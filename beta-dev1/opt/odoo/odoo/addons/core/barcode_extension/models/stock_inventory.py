
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockInventory(models.Model):
    _inherit = 'stock.inventory'

    def on_barcode_scanned(self, barcode):
        product = self.env['product.product'].search([('barcode', '=', barcode)])
        if not product:
            Lot = self.env['stock.production.lot']
            correct_lot = Lot.search([('name','=',barcode)])
            if correct_lot:
                vals = {
                    'prod_lot_id': correct_lot.id,
                    'inventory_id': self.id,
                    'product_id': correct_lot.product_id.id,
                    'product_uom_id': correct_lot.product_id.uom_id.id,
                    'product_qty': correct_lot.product_qty,
                    'location_id': self.location_id.id,
                }
                self.line_ids += self.line_ids.new(vals)
                return
        res = super(StockInventory, self).on_barcode_scanned(barcode)
        return res