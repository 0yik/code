# -*- coding: utf-8 -*-

import logging
from datetime import timedelta
from functools import partial

import psycopg2

from odoo import api, fields, models, tools, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo.http import request
import odoo.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)

class pos_config(models.Model):
    _inherit = 'pos.config' 

    allow_multi_pricing_uom = fields.Boolean('Multi UOM Auto Pricing')

class product_multi_uom(models.Model):
    _inherit = 'product.multi.uom'


    @api.onchange('multi_uom_id')
    def onchange_multi_uom(self):
        if self.multi_uom_id:
            self.price = self.multi_uom_id.factor_inv * self.product_id.lst_price
