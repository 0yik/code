# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
import odoo.addons.decimal_precision as dp

from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, except_orm

from odoo.exceptions import except_orm, UserError, ValidationError

class product_template_inherit(models.Model):
    _inherit = 'product.template'
    
#     min_sale_price = fields.Float('Min Sale Price')
#     max_sale_price = fields.Float('Max Sale Price')
     
    min_sale_price = fields.Float('Min Sale Price', default=0.0, digits=dp.get_precision('Product Price'))
    max_sale_price = fields.Float('Max Sale Price', default=0.0, digits=dp.get_precision('Product Price'))

    @api.constrains('list_price')
    def contrains_list_price(self):
        for record in self:
            if record.list_price > record.max_sale_price or record.list_price < record.min_sale_price:
                raise UserError(_('Sale Price is out of range. Please enter a valid price.'))
 
class sale_order_line_inherit(models.Model):
    _inherit = 'sale.order.line'
       
    @api.onchange('price_unit')
    def onchanger_price_unit(self):
        if self.product_id.max_sale_price > 0.0:
            if self.price_unit < self.product_id.min_sale_price or self.price_unit > self.product_id.max_sale_price:
                raise UserError(_('Sale Price is out of range. Please enter a valid price.'))
#         self.product_id.min_sale_price > 0.0 and 