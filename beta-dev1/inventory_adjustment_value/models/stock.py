from odoo import api, fields, models, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError
from odoo.tools import float_utils

class InventoryLine(models.Model):
    _inherit = 'stock.inventory.line'
    
    price_unit  = fields.Float(string='Unit Price')

# class Inventory(models.Model):
#     _inherit = 'stock.inventory'
# 
#     @api.multi
#     def action_done(self):
#         res = super(Inventory, self).action_done()
#         for line in self.line_ids:
#             line.product_id.standard_price = line.price_unit
#         return res