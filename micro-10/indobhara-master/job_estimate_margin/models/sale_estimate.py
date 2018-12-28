# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import UserError
import odoo.addons.decimal_precision as dp

class SaleEstimateJob(models.Model):
    
    _inherit = "sale.estimate.job"

    expected_margin = fields.Float('Expected Margin')
    duration = fields.Integer('Duration')
    duration_type = fields.Selection([('days','Day(s)'), ('months','Month(s)'), ('years','Year(s)')])

    @api.multi
    def _prepare_quotation_line(self,quotation):
        quo_line_obj = self.env['sale.order.line']
        for rec in self:
            for line in rec.estimate_ids:
                unit_price = (line.price_subtotal + (line.price_subtotal * rec.expected_margin) / 100) / line.product_uom_qty
                vals1 = {
                                'product_id':  line.product_id.id,
                                'product_uom_qty': line.product_uom_qty,
                                'product_uom': line.product_uom.id,
                                'price_unit' : unit_price,
                                'price_subtotal': line.price_subtotal,
                                'name' : line.product_description,
                                'price_total' : self.total,
                                'discount' : line.discount,
                                'order_id':quotation.id,
                                }
                quo_line = quo_line_obj.create(vals1)
            for line in rec.labour_estimate_line_ids:
                unit_price = (line.price_subtotal + (line.price_subtotal * rec.expected_margin) / 100) / line.product_uom_qty
                vals1 = {
                                'product_id':  line.product_id.id,
                                'product_uom_qty': line.product_uom_qty,
                                'product_uom': line.product_uom.id,
                                'price_unit' : unit_price,
                                'price_subtotal': line.price_subtotal,
                                'name' : line.product_description,
                                'price_total' : self.total,
                                'discount' : line.discount,
                                'order_id':quotation.id,
                                }
                quo_line = quo_line_obj.create(vals1)
                
            for line in rec.overhead_estimate_line_ids:
                unit_price = (line.price_subtotal + (line.price_subtotal * rec.expected_margin) / 100) / line.product_uom_qty
                vals1 = {
                                'product_id':  line.product_id.id,
                                'product_uom_qty': line.product_uom_qty,
                                'product_uom': line.product_uom.id,
                                'price_unit' : unit_price,
                                'price_subtotal': line.price_subtotal,
                                'name' : line.product_description,
                                'price_total' : self.total,
                                'discount' : line.discount,
                                'order_id':quotation.id,
                                }
                quo_line = quo_line_obj.create(vals1)
                