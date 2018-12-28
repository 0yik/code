# -*- coding: utf-8 -*-

from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = "stock.picking"

    warehouse_id = fields.Many2one('stock.warehouse', "Warehouse", required=False)
    location_warehouse_id = fields.Many2one('stock.location', "Warehouse", required=False)
    asset_id = fields.Many2one('account.asset.asset', string="Asset")
    internal_usage_menu = fields.Boolean("Internal usage", default=False)

    @api.onchange('internal_usage_menu')
    def onchange_internal_usage_menu(self):
        if self.internal_usage_menu:
            picking_type = self.env['stock.picking.type'].sudo().search([('code','=','internal')], limit=1)
            self.picking_type_id = picking_type.id

    # @api.onchange('location_warehouse_id')
    # def onchange_location_warehouse_id(self):
    #     for move_line in self.move_lines:
    #         if self.location_warehouse_id:
    #             if not move_line.location_warehouse_id:
    #                 stock_quants = self.env['stock.quant'].sudo().search(
    #                     [('location_id', '=', self.location_warehouse_id.id),
    #                      ('product_id', '=', move_line.product_id.id)])
    #                 stock_on_hand = 0
    #                 for stock_quant in stock_quants:
    #                     stock_on_hand += stock_quant.qty
    #                 move_line.stock_on_hand = stock_on_hand
    #         else:
    #             move_line.stock_on_hand = 0
    #             move_line.location_warehouse_id = False



class StockMove(models.Model):
    _inherit = "stock.move"

    @api.depends('product_id','picking_id.location_warehouse_id')
    def compute_product_details(self):
        for rec in self:
            if rec.product_id:
                rec.product_default_code = rec.product_id.default_code
                rec.product_categ_id = rec.product_id.categ_id
            else:
                rec.product_default_code = False
                rec.product_categ_id = False

            if rec.picking_id:
                rec.internal_usage_menu = rec.picking_id.internal_usage_menu

    # @api.depends('product_id','picking_id.location_warehouse_id')
    # def _get_stock_on_hand(self):
    #     for rec in self:
    #         if rec.picking_id.location_warehouse_id:
    #             stock_quants = self.env['stock.quant'].sudo().search([('location_id', '=', rec.picking_id.location_warehouse_id.id),
    #                                                                   ('product_id','=',rec.product_id.id)])
    #             stock_on_hand = 0
    #             for stock_quant in stock_quants:
    #                 stock_on_hand += stock_quant.qty
    #             rec.stock_on_hand = stock_on_hand
    #         else:
    #             rec.stock_on_hand = 0

    internal_usage_menu = fields.Boolean("Internal usage", compute="compute_product_details")
    product_default_code = fields.Char(string="Product Code", compute="compute_product_details")
    product_categ_id = fields.Many2one('product.category', string="Internal Category",)
    stock_on_hand = fields.Float(string="Stock On Hand",)
    product_description_picking = fields.Text(string="Description")
    product_list_price = fields.Float(string="Price",)
    location_warehouse_id = fields.Many2one('stock.location', "Warehouse",)


    @api.onchange('location_warehouse_id')
    def onchange_location_warehouse_id(self):
        if self.location_warehouse_id:
            stock_quants = self.env['stock.quant'].sudo().search(
                [('location_id', '=', self.location_warehouse_id.id),
                 ('product_id', '=', self.product_id.id)])
            stock_on_hand = 0
            for stock_quant in stock_quants:
                stock_on_hand += stock_quant.qty
            self.stock_on_hand = stock_on_hand
        else:
            self.stock_on_hand = 0



    @api.onchange('product_id')
    def onchange_prduct_id_set_price(self):
        self.product_list_price = 0
        self.stock_on_hand = 0
        self.product_description_picking = ''
        if self.product_id:
            self.product_list_price = self.product_id.lst_price
            self.product_description_picking = self.product_id.description_picking
            self.product_categ_id = self.product_id.categ_id


        if self.picking_id.location_warehouse_id:
            stock_quants = self.env['stock.quant'].sudo().search(
                [('location_id', '=', self.picking_id.location_warehouse_id.id),
                 ('product_id', '=', self.product_id.id)])
            stock_on_hand = 0
            for stock_quant in stock_quants:
                stock_on_hand += stock_quant.qty
            self.stock_on_hand = stock_on_hand
        else:
            self.stock_on_hand = 0


class ProductProduct(models.Model):
    _inherit = "product.product"

    @api.multi
    @api.depends('name')
    def name_get(self):
        result = []
        for rec in self:
            if rec.name:
                name = rec.name
                result.append((rec.id, name))
        return result



