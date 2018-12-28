# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from odoo import api, fields, models, tools, _

class inventory_valuation_comparison_sql_report(models.Model):
    _name = "inventory.valuation.comparison.sql.report"
    _auto = False
    
    product_id = fields.Many2one('product.product', 'Product', required=True)
    location_id = fields.Many2one('stock.location', 'Location', required=True)
    sale_order_id = fields.Many2one('sale.order', 'Sale Order')
    so_count = fields.Integer(string='Sale Order Number')
    so_amount = fields.Float(string='Sale Order Amount')
    #PURCHASE
    purchase_id = fields.Many2one('purchase.order', 'Purchase Order')
    po_count = fields.Integer(string='Purchase Order Number')
    po_amount = fields.Float(string='Purchase Order Amount')
    so_po_diff_count = fields.Integer(string='Sales – Purchase')
    so_po_diff_amount = fields.Float(string='Sales – Purchase amount')
    date = fields.Date(string='Date')

    @api.model_cr
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW inventory_valuation_comparison_sql_report as (
            SELECT SBL.id as id,
                PP.id as product_id,
                SBL.location_id as location_id,
                SBL.sale_order_id as sale_order_id,
                SBL.so_count as so_count,
                SBL.so_amount as so_amount,
                SBL.purchase_id as purchase_id,
                SBL.po_count as po_count,
                SBL.po_amount as po_amount,
                SBL.so_po_diff_count as so_po_diff_count,
                SBL.so_po_diff_amount as so_po_diff_amount,
                SBL.date as date
            FROM status_by_location SBL
            left join product_product PP on (PP.id = SBL.status_by_location_id)
            group by
                SBL.id,
                PP.id,
                SBL.status_by_location_id,
                SBL.location_id
            )
        """)
        
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        result = super(inventory_valuation_comparison_sql_report, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
            
        Product = self.env['product.product']
        StatusByLocation = self.env['status.by.location']
        StockMove = self.env['stock.move']
        SaleOrderLine = self.env['sale.order.line']
        PurchaseOrderLine = self.env['purchase.order.line']

        product_objs = Product.search([('active','=',True)])
        print"product_objs",product_objs
        for product_obj in product_objs:#Product.browse(29):#product_objs:29,73
            #print"\nproduct_obj",product_obj
            #print"#SALE.........................................................."
            stock_move_objs = StockMove.search([('product_id','=',product_obj.id),('picking_id.sale_id','!=', False)])
            #print"stock_move_objs",stock_move_objs
            for stock_move_obj in stock_move_objs:
                #print"\nstock_move_obj",stock_move_obj,stock_move_obj.name
                statusbylocation = StatusByLocation.search([
                                                    ('status_by_location_id','=',product_obj.id),
                                                    ('location_id','=',stock_move_obj.location_id.id),
                                                    ('stock_move_id','=',int(stock_move_obj.id)),
                                                    ('sale_order_id','=',stock_move_obj.picking_id.sale_id.id)])
                #print"statusbylocation..",statusbylocation

                so_line_objs = SaleOrderLine.search([
                                                    ('order_id','=',stock_move_obj.picking_id.sale_id.id),
                                                    ('product_id','=',product_obj.id)])
                #print"so_line_objs",so_line_objs

                if statusbylocation:
                    print"Already Created...",statusbylocation
                    for so_line_obj in so_line_objs:
                        statusbylocation.write({
                            'location_id': stock_move_obj.location_id.id,
                            'stock_move_id': int(stock_move_obj.id),
                            'sale_order_id': stock_move_obj.picking_id.sale_id.id,
                            'so_count': so_line_obj.product_uom_qty,
                            'so_amount': so_line_obj.price_subtotal,
                            'so_po_diff_count': (so_line_obj.product_uom_qty) - (statusbylocation.po_count),
                            'so_po_diff_amount': (so_line_obj.price_subtotal) - (statusbylocation.po_amount),
                            'date': stock_move_obj.picking_id.sale_id.confirmation_date.split(" ")[0],
                        })
                else:
                    for so_line_obj in so_line_objs:
                        location = StatusByLocation.search([('stock_move_id','=',int(stock_move_obj.id))])
                        #print"availble ...location",location
                        if not location:
                            vals = {
                                'status_by_location_id': product_obj.id,
                                'location_id': stock_move_obj.location_id.id,
                                'stock_move_id': int(stock_move_obj.id),
                                'sale_order_id': stock_move_obj.picking_id.sale_id.id,
                                'so_count': so_line_obj.product_uom_qty,
                                'so_amount': so_line_obj.price_subtotal,
                                'date': stock_move_obj.picking_id.sale_id.confirmation_date.split(" ")[0],
                            }
                            NewCreated = StatusByLocation.create(vals)
                            #print"\nNewCreated For SO XXXXXXXXXXXXXXXXXX",NewCreated
            

            #print"#PURCHASE..............................................................."
            stock_move_objs = StockMove.search([('product_id','=',product_obj.id),('picking_id.purchase_id','!=', False)])
            #print"\nstock_move_objs PURCHASE.....",stock_move_objs
            for stock_move_obj in stock_move_objs:
                #print"\nstock_move_obj",stock_move_obj,stock_move_obj.name
                statusbylocation = StatusByLocation.search([
                                                    ('status_by_location_id','=',product_obj.id),
                                                    ('location_id','=',stock_move_obj.location_dest_id.id),
                                                    ('stock_move_id','=',int(stock_move_obj.id)),
                                                    ('purchase_id','=',stock_move_obj.picking_id.purchase_id.id)])
                po_line_objs = PurchaseOrderLine.search([('order_id','=',stock_move_obj.picking_id.purchase_id.id),('product_id','=',product_obj.id)])
                #print"po_line_obj",po_line_objs
                if statusbylocation:
                    for po_line_obj in po_line_objs:
                        #print"Already Created...",statusbylocation
                        statusbylocation.write({
                            'location_id': stock_move_obj.location_dest_id.id,
                            'stock_move_id': int(stock_move_obj.id),
                            'purchase_id': stock_move_obj.picking_id.purchase_id.id,
                            'po_count': po_line_obj.product_qty,
                            'po_amount': po_line_obj.price_subtotal,
                            'so_po_diff_count': (statusbylocation.so_count) - (po_line_obj.product_qty),
                            'so_po_diff_amount': (statusbylocation.so_amount) - (po_line_obj.price_subtotal),
                            'date': stock_move_obj.picking_id.purchase_id.date_order.split(" ")[0],
                        })
                else:
                    for po_line_obj in po_line_objs:
                        location = StatusByLocation.search([('stock_move_id','=',int(stock_move_obj.id))])
                        #print"availble ...location",location
                        if not location:
                            vals = {
                                'status_by_location_id': product_obj.id,
                                'stock_move_id': int(stock_move_obj.id),
                                'location_id': stock_move_obj.location_dest_id.id,
                                'purchase_id': stock_move_obj.picking_id.purchase_id.id,
                                'po_count': po_line_obj.product_qty,
                                'po_amount': po_line_obj.price_subtotal,
                                'date': stock_move_obj.picking_id.purchase_id.date_order.split(" ")[0],
                            }
                            NewCreated = StatusByLocation.create(vals)
                            #print"\nNewCreated for POXXXXXXXXXXXXXXXXXX",NewCreated
        return result
        
   
        
    
