# -*- coding: utf-8 -*-


from openerp import api, exceptions, fields, models, _


class ViewProductQty(models.TransientModel):
    _name = 'view.product.qty'

    store_qty = fields.Integer(
        string='Standard Qty On Store', help='Store Qty.')
    stock_qty = fields.Integer(
        string='Current Qty On Warehouse', help='Stock Qty.')


ViewProductQty()
