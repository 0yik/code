from odoo import models, api, fields

class stock_picking(models.Model):
    _inherit = 'stock.picking'

    customer_reference = fields.Char(string='Customer Reference')

class stock_move(models.Model):
    _inherit = 'stock.move'

    description = fields.Text('Description')
    brand = fields.Many2one('product.brand', string="Brand")
    type = fields.Many2one('product.type', string="Product Type")