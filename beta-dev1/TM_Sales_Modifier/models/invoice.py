from odoo import models, fields, api

class invoice(models.Model):
    _inherit = 'account.invoice.line'

    brand = fields.Many2one('product.brand', string='Brand')

    @api.onchange('brand')
    def product_list_brand(self):
        if self.brand:
            return {'domain': {'product_id': [('product_brand_id', '=', self.brand.id)]}}
        else:
            return {'domain': {'product_id': []}}