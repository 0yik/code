from odoo import models, fields, api


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    product_code = fields.Char('Production Code', compute='get_product_code', readonly=False)
    lot_number = fields.Integer('Lot Number')

    @api.one
    @api.depends('product_id.barcode')
    def get_product_code(self):
        self.product_code = self.product_id.barcode


