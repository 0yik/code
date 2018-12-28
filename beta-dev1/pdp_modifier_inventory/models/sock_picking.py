from odoo import models,fields, api

class sale_order(models.Model):
    _inherit = 'stock.picking'

    @api.depends('pack_operation_product_ids')
    def _get_total_price(self):
        for record in self:
            total_price = 0
            for move in record.pack_operation_product_ids:
                if move.product_id and record.product_id.product_tmpl_id:
                    list_price = record.product_id.product_tmpl_id.list_price
                    total_price += list_price * move.qty_done
            record.total_price = total_price

    @api.depends('pack_operation_product_ids')
    def _get_total_quantity(self):
        for record in self:
            total_price = 0
            for move in record.pack_operation_product_ids:
                total_price += move.qty_done
            record.total_quantity = total_price
    total_price = fields.Float('Total Price', compute='_get_total_price')
    total_quantity = fields.Float('Total Quantity', compute='_get_total_quantity')