# -*- coding: utf-8 -*-

from odoo import models, fields, api

class stock_picking(models.Model):
    _inherit = 'stock.picking'

    @api.multi
    def assign_done_value(self):
        for record in self:
            for line in record.pack_operation_product_ids:
                line.qty_done = line.product_qty
