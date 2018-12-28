# -*- coding: utf-8 -*-

from openerp import api, exceptions, fields, models, _


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    qty_store = fields.Integer(
        string='Standard Qty On Store', help='Standard Qty On Store.')
    qty_stock = fields.Integer(
                string='Current Qty On Warehouse', help='Stock Qty.', )
    current_qty_store = fields.Integer(
                string='Current Qty On Store', help='New qty on hand from store qty pop-up', )
    standard_qty_warehouse = fields.Integer(
                string='Standard Qty Warehouse', help='Set qty Set Standard Qty Warehouse from onhand pop-up', )
    view_stock_line_ids = fields.One2many(
        comodel_name='view.stock.line',
        inverse_name='sale_line_id', string='View Stock', help='Stock View.')

    #current_qty_store = qty on hand on store (new qty on hand from store qty pop-up)
    #standard_qty_warehouse = qty on hand (set qty Set Standard Qty Warehouse from onhand pop-up)

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()
        if not self.product_id:
            self.update({
                'qty_store': 0,
                'qty_stock': 0,
                'view_stock_line_ids': False,
            })
            return res
        vals = {}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = 1.0
        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id)
        vals.update({'qty_store': product.qty_min_store,
                     'qty_stock': product.qty_available,
                     'current_qty_store': 1,
                     'standard_qty_warehouse': 1,
                     'view_stock_line_ids': [[0, 0, {
                     'qty_store': product.qty_min_store,
                     'qty_stock': product.qty_available,
                     'current_qty_store': product.qty_new_store,
                     'standard_qty_warehouse': product.qty_warehouse,
                        }]]
                     })
        self.update(vals)
        return res


SaleOrderLine()

class ViewStockLine(models.Model):
    _name = 'view.stock.line'
    _description = 'View Stock Line'

    sale_line_id = fields.Many2one(
        comodel_name='sale.order.line', string='Sale Line', help='ref. sale line')
    qty_store = fields.Integer(
        string='Standard Qty On Store', help='Standard Qty On Store.')
    qty_stock = fields.Integer(
                string='Current Qty On Warehouse', help='Stock Qty.', )
    current_qty_store = fields.Integer(
                string='Current Qty On Store', help='New qty on hand from store qty pop-up', )
    standard_qty_warehouse = fields.Integer(
                string='Standard Qty Warehouse', help='Set qty Set Standard Qty Warehouse from onhand pop-up', )


