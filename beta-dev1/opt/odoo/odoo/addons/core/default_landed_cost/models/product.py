from odoo import fields,models,api, _

class product_template(models.Model):
    _inherit = 'product.template'

#     product_id = fields.Many2one('product.product','Product')
    product_ids = fields.Many2many('product.product', string='Product')




