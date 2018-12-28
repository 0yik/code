# -*- coding: utf-8 -*-
import time
from datetime import datetime
from odoo import models, fields, api
from odoo.tools.translate import _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta

class res_partner(models.Model):
    _inherit = "res.partner"

    product_ids = fields.Many2many('product.template', 'ppd_partner_product_rel', 'product_id', 'partner_id',string='Product')

res_partner()

class product_template(models.Model):
    _inherit = "product.template"

    def _qty_to_produce(self):
        res = {}
        for line in self:
            qty_to_produce = 0.0
            res[line.id] = 0.0
            qty_to_produce = line.virtual_available - line.par_level
            if qty_to_produce > 0.0:
                qty_to_produce = 0.0
            res[line.id] = qty_to_produce
        return res

    partner_ids = fields.Many2many('res.partner', 'ppd_partner_product_rel', 'partner_id', 'product_id',string='Partner')
    par_level = fields.Float('Par Level')
    qty_to_produce = fields.Float(compute='_qty_to_produce', string="Qty to Produce", readonly=True)

product_template()