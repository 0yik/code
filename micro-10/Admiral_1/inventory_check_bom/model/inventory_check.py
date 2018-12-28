# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import  datetime

class InventoryCheck(models.Model):
    _inherit = 'inventory.check'
    string_stock_quant = fields.Char('Quantity on Hand')
    @api.model
    def add_inventory_check_lines(self, product_id):
        ProductTemplate = self.env['product.template']
        stock_quant_list = []
        purchase_order_income_list = []
        last_sold_list = []
        last_purchase_list = []
        product_list = [ProductTemplate.browse(product_id).id]

        product_product_id = self.env['product.product'].search([('name','=',ProductTemplate.browse(product_id).name)])[0]

        stock_quant_ids = self.env['stock.quant'].search(
            [('product_id', '=', product_product_id.id),('location_id.usage','=','internal')])

        stock_name = {}
        array_stock_name = []

        if stock_quant_ids:


            for sq in stock_quant_ids:
                location_name = sq.location_id.name_get()[0][1]
                qty = sq.qty

                if stock_name.get(location_name, False):
                    st_qty = stock_name.get(location_name)
                    stock_name.update({location_name: qty + st_qty })
                else:
                    stock_name.update({location_name: qty})
        for key, val in stock_name.iteritems():
            array_stock_name.append(str(val) + ' - ' + key)

        purchase_order_ids = self.env['purchase.order.line'].search([('product_id', '=', product_id), ('state', '=', 'purchase')]).mapped('order_id')

        if purchase_order_ids:
            for po in purchase_order_ids:
                if po.picking_ids[0].state != 'done':
                    purchase_order_income_list.append(po.id)
            purchase_order_income_list = list(set(purchase_order_income_list))
        purchase_order_last = self.env['purchase.order.line'].search(
            [('product_id', '=', product_id), ('state', '=', 'purchase')]).sorted('confirm_date', reverse=True)
        if purchase_order_last:
            last_purchase_list.append(
                (purchase_order_last[0].currency_id.symbol, str(purchase_order_last[0].price_unit)))
        sale_order_last = self.env['sale.order.line'].search(
            [('product_id', '=', product_id), ('state', '=', 'sale')]).sorted('confirm_date', reverse=True)
        if sale_order_last:
            last_sold_list.append((sale_order_last[0].currency_id.symbol, str(sale_order_last[0].price_unit)))

        max_length = max(len(last_sold_list), len(last_purchase_list), len(product_list), len(array_stock_name),
                         len(purchase_order_income_list))

        for count in range(max_length):
            name = stock_quant_id = purchase_order_id = last_sold_price = last_purchase_price = incomming_qty = False

            if count < len(product_list):
                name = product_list[count]
            if count < len(array_stock_name):
                stock_quant_id = array_stock_name[count]
            if count < len(purchase_order_income_list):
                purchase_order_id = purchase_order_income_list[count]
                incomming_quantity = self.env['purchase.order.line'].search([('order_id','=',purchase_order_id)])
                for line in incomming_quantity:
                    if line.product_id.id == product_id:
                        incomming_qty = line.product_qty
            if count < len(last_sold_list):
                last_sold_price = last_sold_list[count]
            if count < len(last_purchase_list):
                last_purchase_price = last_purchase_list[count]
            vals = {
                'name': name,
                'string_stock_quant': stock_quant_id,
                'purchase_order_id': purchase_order_id,
                'incomming_quantity': incomming_qty,
                'last_sold_price': last_sold_price and last_sold_price[0] + " " + last_sold_price[1] or '',
                'last_purchase_price': last_purchase_price and last_purchase_price[0] + " " + last_purchase_price[
                    1] or '',
            }

            self.create(vals)

    @api.model
    def create_new_inventory(self, product_id, is_bom, context=None):
        self.search([]).unlink()
        product = self.env['product.template'].browse(product_id)
        if product:
            boms = self.env['mrp.bom'].search([('product_tmpl_id', '=', product_id)])
            product_template_ids = [product_id]

            if is_bom:
                for bom in boms:
                    for line in bom.bom_line_ids:
                        product_template_id = line.product_id.product_tmpl_id and line.product_id.product_tmpl_id.id
                        if product_template_id not in product_template_ids:
                            product_template_ids.append(product_template_id)
            for product_template_id in product_template_ids:
                self.add_inventory_check_lines(product_template_id)

    @api.model
    def create_new_product(self, product_id, context=None):
        return

InventoryCheck()