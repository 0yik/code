# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class stock_picking(models.Model):
    _inherit = "stock.picking"

    @api.multi
    def action_get_stock_logs(self):
        stock_operation_log = self.env['stock.operation.log'].search([('is_check', '=', False)], order="id desc",
                                                                     limit=1)
        if stock_operation_log and stock_operation_log.rfid:
            product_id = self.env['product.product'].search([('rfid', '=', stock_operation_log.rfid)], limit=1)
            stock_pack_operation = self.pack_operation_product_ids.filtered(
                lambda r: r.product_id.id == stock_operation_log.product_id.id)
            correct_lot = self.env['stock.production.lot'].search([('name', '=', stock_operation_log.rfid)], limit=1)
            if product_id:
                if stock_pack_operation:
                    stock_pack_operation.qty_done +=1
                    stock_pack_operation.scanned_rfid = stock_operation_log.rfid
                    stock_operation_log.is_check = True
                else:
                    pack_vals = {
                        'product_id': product_id.id,
                        'product_uom_id': product_id.uom_id.id,
                        'product_qty': correct_lot.product_qty,
                        'qty_done': 0,
                        'location_id': self.location_id.id,
                        'location_dest_id': self.location_dest_id.id,
                        'date': fields.Datetime.now(),
                        'scanned_rfid': stock_operation_log.rfid,
                    }
                    operation = self.pack_operation_product_ids.new(pack_vals)
                    self.pack_operation_product_ids += operation
                    stock_operation_log.is_check = True

            else:
                stock_operation_log.is_check = True
                raise ValidationError(
                    _('The RFID code "%s" doesnt correspond to a proper product, package or location.') % (
                    stock_operation_log.rfid))


class stock_pack_operation(models.Model):
    _inherit = "stock.pack.operation"

    recommended_rfid = fields.Char('Recommended RFID Barcodes', compute="_get_rfid_code")
    scanned_rfid = fields.Char('Scanned RFID Barcodes', readonly=True)

    @api.one
    @api.multi
    def _get_rfid_code(self):
        self.recommended_rfid = self.product_id.rfid


