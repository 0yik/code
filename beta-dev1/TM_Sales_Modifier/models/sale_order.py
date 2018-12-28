from odoo import models, fields, api

class sale_order(models.Model):
    _inherit = 'sale.order.line'

    brand = fields.Many2one('product.brand', string='Brand')

    @api.onchange('brand')
    def product_list_brand(self):
        if self.brand:
            return {'domain': {'product_id': [('product_brand_id', '=', self.brand.id)]}}
        else:
            return {'domain': {'product_id': []}}