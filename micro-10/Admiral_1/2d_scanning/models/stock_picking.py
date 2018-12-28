# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def on_barcode_scanned(self, barcode):
        Product = self.env['product.product']
        Lot = self.env['stock.production.lot']
        Picking_Line = self.env['stock.pack.operation']
        Pack_Line = self.env["stock.pack.operation.lot"]

        location = self.env['stock.location'].search([('barcode', '=', barcode)])

        if location:
            self.location_dest_id = location[0]
            return

        correct_product = Product.search(['|', ('barcode', '=', barcode), ('default_code', '=', barcode)])

        if not correct_product and self.picking_type_id.code in ['outgoing', 'internal'] and self.state in [
            'partially_available', 'assigned']:
            correct_lot = Lot.search([('name', '=', barcode)], limit=1)
            # Admiral generated 2d barcode like '8934974151265\,9786041109056\,2018\-05\-31'. We need to get correct lot/serial number of product.
            if '\,' in barcode and not correct_lot:
                twod_code = barcode.split('\,')
                for code in twod_code:
                    correct_lot = Lot.search([('name', '=', code)], limit=1)
                    if correct_lot:
                        barcode = code
                        break

            if correct_lot:
                lot_product = correct_lot.product_id
                correct_line = self.pack_operation_product_ids.filtered(lambda r: r.product_id.id == lot_product.id)
                if correct_line:
                    pack_line_vals = {
                        'qty': 1,
                        'lot_name': barcode,
                        'operation_id': correct_line[0].id,
                        'lot_id': correct_lot[0].id,
                    }
                    existed_line = Pack_Line.search([
                        ('operation_id', '=', correct_line[0].id),
                        ('lot_id', '=', correct_lot[0].id),
                    ], limit=1)
                    if existed_line and existed_line.id:
                        if existed_line.qty > 0:
                            return {'warning': {
                                'title': _('You have entered this serial number already'),
                                'message': _('You have already scanned the serial number "%(barcode)s"') % {
                                    'barcode': barcode},
                            }}
                        existed_line.action_add_quantity(1)
                    else:
                        Pack_Line.create(pack_line_vals).id

                    return {
                        'value': {
                            'picking_scaned_barcode': barcode
                        }
                    }
                pack_vals = {
                    'product_id': correct_lot.product_id.id,
                    'product_uom_id': correct_lot.product_id.uom_id.id,
                    'product_qty': correct_lot.product_qty,
                    'qty_done': 0,
                    'location_id': self.location_id.id,
                    'location_dest_id': self.location_dest_id.id,
                    'date': fields.Datetime.now(),
                }
                self.pack_operation_product_ids += self.pack_operation_product_ids.new(pack_vals)
                return {'value': {'picking_scaned_barcode': barcode}}
        res = super(StockPicking, self).on_barcode_scanned(barcode)
        return res
