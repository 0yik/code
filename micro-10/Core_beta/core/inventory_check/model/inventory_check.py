# -*- coding: utf-8 -*-

from odoo import api, fields, models
from datetime import  datetime

class StockQuant(models.Model):

    _inherit = "stock.quant"

    @api.multi
    def name_get(self):
        if self._context and self._context.get('tree_inventory_quickadd_view_ref', False):
            result = []
            for record in self:
                name = "%s - %s" % (record.qty, record.location_id.name_get()[0][1])
                result.append((record.id, name))
        else:
            result= super(StockQuant, self).name_get()
        return result

class PurchaseOrder(models.Model):

    _inherit = "purchase.order"

    @api.multi
    def name_get(self):
        if self._context and self._context.get('tree_inventory_quickadd_view_ref', False):
            result = []
            for record in self:
                name =  record.name
                result.append((record.id, name))
        else:
            result = super(PurchaseOrder, self).name_get()
        return result

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    confirm_date = fields.Datetime('Confirm Date', related='order_id.date_order')

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    confirm_date = fields.Datetime('Confirm Date', related='order_id.confirmation_date')

class Manufacturing(models.Model):
    _inherit = 'mrp.production'

    @api.multi
    def name_get(self):
        if self._context and self._context.get('tree_inventory_quickadd_view_ref', False):
            result = []
            for record in self:
                name = record.name
                qty = record.product_qty
                full_name = str(qty) + '-' + name
                result.append((record.id, full_name))
        else:
            result = super(Manufacturing, self).name_get()
        return result


class InventoryCheck(models.Model):
    _name = 'inventory.check'

    name = fields.Many2one('product.template', string='Product')
    stock_quant_id = fields.Many2one('stock.quant', string='Quantity per Location')
    purchase_order_id = fields.Many2one('purchase.order', string='Incoming Orders ')
    last_sold_price = fields.Char(string='Last Sold Price')
    last_purchase_price = fields.Char(string='Last Purchased Price')
    incomming_quantity = fields.Char(string='Incoming Quantity')
    mrp_production_id = fields.Many2one('mrp.production', string="Manufacturing")
    qty_on_hand = fields.Char('Quantity On Hand')
    scheduled_date = fields.Char('Scheduled Date')

    # @api.model
    # def list_products(self, context=None):
    #     ng = dict(self.env['product.template'].name_search('',[]))
    #     ids = ng.keys()
    #     result = []
    #     for product in self.env['product.template'].browse(ids):
    #         result.append((product.id,ng[product.id]))
    #     return result

    @api.model
    def list_products(self, context=None):
        result = []
        for product in self.env['product.template'].search([]):
            if product.id and product.name:
                result.append((product.id, product.name))
        return result

    @api.model
    def search_read(self, domain=None, fields=None, offset=0, limit=None, order=None):
        res = super(InventoryCheck, self).search_read(domain=domain, fields=fields, offset=offset,
                                                  limit=limit, order=order)
        return res

    @api.model
    def create_new_product(self, product_id, context=None):
        self.search([]).unlink()
        if product_id > 0:
            ProductTemplate = self.env['product.template']
            stock_quant_list = []
            purchase_order_income_list = []
            last_sold_list = []
            last_purchase_list = []
            mrp_product_list = []
            po_scheduled_date = []
            product_list = [ProductTemplate.browse(product_id).id]
            stock_quant_ids = self.env['stock.quant'].search([('product_id','=', product_id), ('location_id.usage','=', 'internal')])
            if stock_quant_ids:
                for sq in stock_quant_ids:
                    stock_quant_list.append(sq.id)
            total = 0
            for stock_quant_id in stock_quant_ids:
                total = total + stock_quant_id.qty
            purchase_order_ids = self.env['purchase.order.line'].search([('product_id', '=', product_id), ('state','=','purchase')]).mapped('order_id')
            if purchase_order_ids:
                for po in purchase_order_ids:
                    po_scheduled_date.append(po.date_planned)
                    purchase_order_income_list.append(po.id)
                purchase_order_income_list = list(set(purchase_order_income_list))
            purchase_order_last = self.env['purchase.order.line'].search([('product_id', '=', product_id), ('state','=','purchase')]).sorted('confirm_date', reverse=True)
            if purchase_order_last:
                last_purchase_list.append((purchase_order_last[0].currency_id.symbol, str(purchase_order_last[0].price_unit)))
            sale_order_last = self.env['sale.order.line'].search([('product_id', '=', product_id), ('state', '=', 'sale')]).sorted('confirm_date', reverse=True)
            if sale_order_last:
                last_sold_list.append((sale_order_last[0].currency_id.symbol,str(sale_order_last[0].price_unit)))
            mrp_production_ids = self.env['mrp.production'].search([('product_id', '=', product_id), ('state', '=', 'progress')])

            max_length = max(len(last_sold_list), len(last_purchase_list), len(product_list), len(stock_quant_list), len(purchase_order_income_list),len(mrp_product_list),len(po_scheduled_date))
            name_check = []
            for count in range(max_length):
                name = stock_quant_id = purchase_order_id = last_sold_price = last_purchase_price = total_qty = scheduled_date =False
                if count < len(product_list):
                    name = product_list[count]
                if count < len(stock_quant_list):
                    stock_quant_id = stock_quant_list[count]
                if count < len(purchase_order_income_list):
                    purchase_order_id = purchase_order_income_list[count]
                if count < len(last_sold_list):
                    last_sold_price = last_sold_list[count]
                if count < len(last_purchase_list):
                    last_purchase_price = last_purchase_list[count]
                # if count < len(mrp_product_list):
                #     mrp_product_list = mrp_product_list[count]
                if count < len(po_scheduled_date):
                    scheduled_date = po_scheduled_date[count]
                if count < 1:
                    total_qty = total
                vals = {
                    'name' : name,
                    'stock_quant_id' : stock_quant_id,
                    'purchase_order_id' : purchase_order_id,
                    'last_sold_price' : last_sold_price and last_sold_price[0] +" "+last_sold_price[1] or '',
                    'last_purchase_price' : last_purchase_price and last_purchase_price[0]+" "+last_purchase_price[1] or '',
                    'qty_on_hand': total_qty,
                    'scheduled_date':scheduled_date,
                }
                if mrp_production_ids:
                    for mrp_production_id in mrp_production_ids:
                        if mrp_production_id.product_id.id == name:
                            if name in name_check:
                                vals['name'] = False
                            vals.update({'mrp_production_id': mrp_production_id.id})

                            self.create(vals)
                else:
                    self.create(vals)

InventoryCheck()