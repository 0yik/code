
from odoo import models, fields, api


class Product_product(models.Model):
    _inherit = "product.template"

    is_an_equipment = fields.Boolean('Is An Equipment')
