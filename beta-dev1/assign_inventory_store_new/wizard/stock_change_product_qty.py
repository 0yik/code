# -*- coding: utf-8 -*-

from odoo import api, models, fields, tools, _
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError


class ProductChangeQuantity(models.TransientModel):
    _inherit = 'stock.change.product.qty'

    qty_warehouse_new = fields.Integer(
        'Set Standard Qty Warehouse',default=1,
        digits=dp.get_precision('Product Unit of Measure'), required=True,
        help='Qty Warehouse.')

    @api.model
    def default_get(self, fields):
        res = super(ProductChangeQuantity, self).default_get(fields)
        if self.env.context.get('active_id') and self.env.context.get('active_model') == 'product.template':
            res['qty_warehouse_new'] = self.env['product.product'].search(
                [('product_tmpl_id', '=', self.env.context['active_id'])], limit=1).qty_warehouse
        elif self.env.context.get('active_id') and self.env.context.get('active_model') == 'product.product':
            res['qty_warehouse_new'] = self.env['product.product'].browse(self.env.context['active_id']).qty_warehouse
        return res #super(ProductChangeQuantity, self).default_get(fields)

    @api.multi
    def change_product_qty(self):
        res = super(ProductChangeQuantity, self).change_product_qty()
        for wizard in self:
            wizard.product_id.write({
                'qty_warehouse': wizard.qty_warehouse_new,
            })
        return res


ProductChangeQuantity()
