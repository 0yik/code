from odoo import api, fields, models
from odoo import api, fields, models, tools, _

class product_template(models.Model):
    _inherit = 'sale.order.line'

    property = fields.Many2one('product.category', 'Property')