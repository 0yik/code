# -*- coding: utf-8 -*-

from odoo import models, fields, api

class stock_location_inherit(models.Model):
    _inherit = 'sale.order'

    def inventory_summary_button(self):
        product_ids = []
        product = []
        locations_ids = []
        locations = []
        inventory_summary = []
        for order_line in self.order_line:
            if order_line.product_id.id not in product:
                product_ids.append(order_line.product_id)
                product.append(order_line.product_id.id)
        locations_obj_ids  = self.env['stock.location'].search([('inventory_summary','=',True)])
        for locations_obj in locations_obj_ids:
            locations_ids.append(locations_obj)
            if locations_obj.location_id:
                display_name_location = '%s/%s' % (locations_obj.location_id.name, locations_obj.name)
            else:
                display_name_location = locations_obj.name
            locations.append(display_name_location)

        for product in product_ids:
            quantity = []
            total_qty = 0
            required_qty = 0
            for locations_id in locations_ids:
                qty = 0
                inventory_obj = self.env['stock.quant'].search([('product_id', '=', product.id),('location_id','=',locations_id.id)])
                if inventory_obj:
                    for inventory in inventory_obj:
                        qty += inventory.qty
                quantity.append(qty)
                total_qty += qty

            for order_line in self.order_line:
                if order_line.product_id.id == product.id:
                    required_qty += order_line.product_uom_qty

            quantity.append(required_qty)
            quantity.append(total_qty)

            inventory_summary.append({'product_name': product.name, 'quantity' : quantity})

        return {
            'type': 'ir.actions.act_window',
            'name': 'inventory summary',
            'view_type': 'form',
            'view_mode': 'form',
            'context':{'locations_ids': locations,'inventory_summary':inventory_summary},
            'res_model': 'inventory.summary',
            'target': 'new',
        }

class sales_order_line_inherit(models.Model):
    _inherit = "sale.order.line"

    def inventory_summary_button(self):
        locations_ids = []
        locations = []
        inventory_summary = []
        locations_obj_ids  = self.env['stock.location'].search([('inventory_summary','=',True)])
        for locations_obj in locations_obj_ids:
            locations_ids.append(locations_obj)
            if locations_obj.location_id:
                display_name_location = '%s/%s' % (locations_obj.location_id.name, locations_obj.name)
            else:
                display_name_location = locations_obj.name
            locations.append(display_name_location)

        for product in self.product_id:
            quantity = []
            total_qty = 0
            for locations_id in locations_ids:
                qty = 0
                inventory_obj = self.env['stock.quant'].search([('product_id', '=', product.id),('location_id','=',locations_id.id)])
                if inventory_obj:
                    for inventory in inventory_obj:
                        qty += inventory.qty
                quantity.append(qty)
                total_qty += qty

            quantity.append(self.product_uom_qty)
            quantity.append(total_qty)

            inventory_summary.append({'product_name': product.name, 'quantity' : quantity})

        return {
            'type': 'ir.actions.act_window',
            'name': 'inventory summary',
            'view_type': 'form',
            'view_mode': 'form',
            'context':{'locations_ids': locations,'inventory_summary':inventory_summary},
            'res_model': 'inventory.summary',
            'target': 'new',
        }
class inventory_summary_inherit(models.TransientModel):
    _name = 'inventory.summary'