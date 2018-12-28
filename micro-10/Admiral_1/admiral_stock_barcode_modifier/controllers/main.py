# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.stock_barcode.controllers.main import StockBarcodeController

class StockBarcodeControllerInherit(StockBarcodeController):
    def try_new_internal_picking(self, barcode):
        """ If barcode represents a location, open a new picking from this location
        """
        corresponding_location = request.env['stock.location'].search([
            ('barcode', '=', barcode),
            ('usage', '=', 'internal')
        ], limit=1)
        if corresponding_location:
            internal_picking_type = request.env['stock.picking.type'].search([('code', '=', 'internal')])
            warehouse = corresponding_location.get_warehouse()
            if warehouse:
                internal_picking_type = internal_picking_type.filtered(lambda r: r.warehouse_id == warehouse)
            dest_loc = corresponding_location
            while dest_loc.location_id and dest_loc.location_id.usage == 'internal':
                dest_loc = dest_loc.location_id
            if internal_picking_type:
                # Create and confirm an internal picking
                picking = request.env['stock.picking'].create({
                    'picking_type_id': internal_picking_type[0].id,
                    'location_id': corresponding_location.id,
                    'location_dest_id': dest_loc.id,
                })

                # Open its form view
                action_picking_form = request.env.ref('stock_barcode.stock_picking_action_form')
                action_picking_form = action_picking_form.read()[0]
                action_picking_form.update(res_id=picking.id)
                return {'action': action_picking_form}
            else:
                return {'warning': _('No internal picking type. Please configure one in warehouse settings.')}
        return False
