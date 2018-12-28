# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError, RedirectWarning, ValidationError

class sales_order(models.Model):
    _inherit = 'sale.order'

    @api.one
    @api.constrains('order_line')
    def _check_discounts(self):
        ''' To check the total weightage and raises validation error, if total is not 100.'''
        total = [x.price_unit for x in self.order_line if x.product_id]
        total = total and sum(total)
        if self.discount_rate > total*0.2:
            raise ValidationError("Discount can't be greater than 20%% of Total ($ %.2f)" % (total*0.2))
