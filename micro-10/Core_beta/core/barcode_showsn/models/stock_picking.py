# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class StockPicking(models.Model):
    _inherit= 'stock.picking'

    def on_barcode_scanned(self, barcode):
        Product   = self.env['product.product']
        Lot       = self.env['stock.production.lot']

        correct_product = Product.search(['|', ('barcode', '=', barcode), ('default_code', '=', barcode)])

        if not correct_product and self.picking_type_id.code in ['outgoing', 'internal'] and self.state in ['partially_available', 'assigned']:
            lots = Lot.search([('name', '=', barcode)], limit=1)
            if lots:
                lot          = lots[0]
                lot_product  = lot.product_id
                opperations  = self.pack_operation_product_ids.filtered(lambda r: r.product_id.id == lot_product.id)
                if opperations:
                    opperation = opperations[0]

                    packs = opperation.pack_lot_ids.filtered(lambda r: r.lot_id.id == lot.id)
                    if packs:
                        message = {}
                        if packs.qty >= 1:
                            message = {
                                'warning': {
                                    'title': _('You have entered this serial number already'),
                                    'message': _(
                                        'You have already scanned the serial number "%(barcode)s"') % {'barcode': barcode},
                                }
                            }
                        else:
                            packs.do_plus()
                            message = {}
                        return message

        res = super(StockPicking, self).on_barcode_scanned(barcode)
        return res