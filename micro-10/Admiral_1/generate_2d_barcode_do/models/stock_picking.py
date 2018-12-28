# -*- coding: utf-8 -*-

from odoo import models, fields, api
import re
from datetime import datetime
import pytz
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT



class DeliveryOrder(models.Model):
    _inherit = 'stock.picking'

    def generate_qr_code(self):
        data = []
        now = datetime.now()
        user_tz = self.env.user.tz or 'Singapore'
        local = pytz.timezone(user_tz)
        now = pytz.utc.localize(now).astimezone(local).strftime(DEFAULT_SERVER_DATETIME_FORMAT)
        for pack_line in self.pack_operation_product_ids:

            for lot_line in pack_line.pack_lot_ids:
                if pack_line.product_id and pack_line.product_id.barcode:
                    code = pack_line.product_id.barcode + ',' + lot_line.lot_id.name + ','
                else:
                    code = lot_line.lot_id.name + ','

                if lot_line.lot_id and lot_line.lot_id.use_date:
                    code += str(lot_line.lot_id.use_date)[0:10]
                data.append({
                    'code'   : str(re.escape(code)),
                    'product': pack_line.product_id.name,
                    'barcode': pack_line.product_id.barcode if pack_line.product_id.barcode else '',
                    'lot'    : lot_line.lot_id.name,
                    'expiry_date': lot_line.lot_id.use_date,
                    'date' : now
                })
        return data

    def serialize_and_validate(self):
        self.action_product_to_serializer()
        self.do_new_transfer()
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'generate_2d_barcode_do.qrcode_label',
            'report_type': 'qweb-pdf',
        }

    @api.multi
    def do_new_transfer(self):
        super(DeliveryOrder, self).do_new_transfer()
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'generate_2d_barcode_do.qrcode_label',
            'report_type': 'qweb-pdf',
        }

class ProductTemplate(models.Model):
    _inherit = 'product.template'

    barcode = fields.Char(required=True)

