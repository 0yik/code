# -*- coding: utf-8 -*-
from odoo import api, fields, models, _

class StockMove(models.Model):
    _inherit = "stock.move"


    @api.depends('product_id')
    def _get_product_code(self):
        for record in self:
            if record.product_id:
                record.code = record.product_id.product_tmpl_id.code

    code = fields.Char(string='Product Code', compute='_get_product_code')
