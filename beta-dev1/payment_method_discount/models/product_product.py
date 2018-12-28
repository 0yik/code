from odoo import api, fields, models, tools, _


class ProductProduct(models.Model):
    _inherit = "product.product"

    is_discount_product = fields.Boolean(string = "POS Discount Product", default=False)
