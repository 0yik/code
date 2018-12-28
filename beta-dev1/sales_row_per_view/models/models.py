# -*- coding: utf-8 -*-

from odoo import models, fields, api

class sales_row_per_view(models.Model):
    _inherit = 'sale.order'
    l=80
    @api.multi
    def get_limit(self):
        self.limit =2
        l=2
    limit=fields.Integer(compute=get_limit)
    rows=fields.Integer(string="Rows",default=80)
    order_line = fields.One2many('sale.order.line', 'order_id', string='Order Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)

    # @api.multi
    # def write(self, vals):
    #     return super(sales_row_per_view, self).write(vals)

# class SaleOrderLine(models.Model):
#     _inherit = 'sale.order.line'
#     proxy_order_id = fields.Many2one('sale.order', string='Order Reference', required=True, ondelete='cascade', index=True, copy=False)