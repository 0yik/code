# -*- coding: utf-8 -*-
# See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = 'product.product'

    @api.model
    def get_products_by_pricelist(self, product_ids = None, pricelist_ids = None,):
        """
        It will calculate the price of the products based on pricelist.
        @return: dictionary of dictionary {pricelist_id: {product_id: price}}
        """
        pricelist_obj = self.env['product.pricelist']
        product_price_res = {}
        if not pricelist_ids:
            pricelist_ids = pricelist_obj.sudo().search([]).sudo().ids
        elif isinstance( pricelist_ids, int ):
            pricelist_ids = [pricelist_ids]
        if not product_ids:
            product_ids = self.sudo().search([( 'available_in_pos', '=', True ), ( 'sale_ok', '=', True )]).sudo().ids
        elif isinstance( product_ids, int ):
            product_ids = [product_ids]
        for pricelist_id in pricelist_ids:
            product_price_res.update( {pricelist_id: {}} )
            for product_id in product_ids:
                price = pricelist_obj.price_get(product_id, 1.0)[pricelist_id]
                product_price_res[pricelist_id].update( {product_id: price} )
        return product_price_res


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def _order_fields(self, ui_order):
        order_fields = super(PosOrder, self)._order_fields(ui_order)
        order_fields['pricelist_id'] = ui_order.get( 'pricelist_id', False )
        return order_fields
