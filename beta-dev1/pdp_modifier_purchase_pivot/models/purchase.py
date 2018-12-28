from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT

from datetime import datetime
from dateutil.relativedelta import relativedelta

    
class product_product(models.Model):
    _inherit = 'product.product'

    brand_id = fields.Many2one('brand.brand','Brand')
    
    
class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    brand_id = fields.Many2one('brand.brand','Brand')
    
    @api.onchange('product_id')
    def onchange_product_id(self):
        if self.product_id:
            if self.product_id.brand_id:
                self.brand_id = self.product_id.brand_id
            else:
                self.brand_id = False
        res = super(PurchaseOrderLine, self).onchange_product_id()
        return res





