from odoo import models, fields, api

class ProductRepacking(models.TransientModel):
    _name = 'product.repacking'
    _description = 'Product Repacking'

    product_id = fields.Many2one('product.product', string='Product')
    lot_id = fields.Many2one('stock.production.lot', string='Lot')
    batch_no = fields.Char(related='lot_id.display_batch_no', string='Batch No')
    bbd = fields.Datetime(related='lot_id.display_bbd', string='Best Before Date')
    repack_product_id = fields.Many2one('product.product', string='Product')
    tracking = fields.Selection(related='product_id.tracking', readonly=True, string='Product Tracking')

    @api.onchange('product_id')
    def onchage_lot(self):
        self.lot_id = False
        self.repack_product_id = False

    @api.multi
    def print_label(self):
        return self.env['report'].get_action(self, 'helaspice_receiving_import.report_repacking_label')

ProductRepacking()