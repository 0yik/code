from odoo import models, fields, api

class ManageIncomingBatch(models.Model):
    _name = 'manage.incoming.batch'
    _description = 'Manage Incoming Batch'
    _rec_name = 'lot_id'
    _order = 'id desc'

    @api.multi
    def _compute_done_qty(self):
        for record in self:
            qty = 0
            for pick_id in record.picking_ids.filtered(lambda pick: pick.state == 'done'):
                for pack_id in pick_id.pack_operation_product_ids.filtered(lambda pack: pack.product_id == record.product_id):
                    if pack_id.product_id.tracking == 'none':
                        qty += pack_id.qty_done
                    else:
                        qty += sum(pack_id.pack_lot_ids.filtered(lambda lot: lot.lot_id == record.lot_id).mapped('qty'))
            record.done_qty = qty

    @api.depends('lot_id', 'lot_id.use_date', 'lot_id.actual_bbd', 'lot_id.batch_no', 'lot_id.actual_batch_no')
    def compute_batch_bbd(self):
        for record in self:
            lot_id = record.lot_id
            if lot_id:
                record.use_date = lot_id.use_date if not lot_id.actual_bbd else lot_id.actual_bbd
                record.batch_no = lot_id.batch_no if not lot_id.actual_batch_no else lot_id.actual_batch_no
            else:
                record.use_date = False
                record.batch_no = False

    product_id = fields.Many2one('product.product', required=True, readonly=True, string='Product')
    origin = fields.Char(string='Reference', readonly=True)
    shipment_id = fields.Many2one('shipment.reference', readonly=True, string='Shipment')
    pallet_no = fields.Integer(readonly=True, string='Pallet No')
    po_reference = fields.Char(readonly=True, string='PO Reference')
    picking_ids = fields.Many2many('stock.picking', string='Shipping Reference')
    lot_id = fields.Many2one('stock.production.lot', required=False, readonly=True, string='Lot/Serial No')
    use_date = fields.Datetime(compute='compute_batch_bbd', string='Best Before Date')
    batch_no = fields.Char(compute='compute_batch_bbd', string='Batch No')
    qty = fields.Float(string='Forecasted Qty', readonly=True)
    done_qty = fields.Float(compute='_compute_done_qty', string='Received Qty')

ManageIncomingBatch()

class ShipmentReference(models.Model):
    _name = 'shipment.reference'
    _description = 'Shipment Rerence'
    _order = 'id desc'

    name = fields.Char(required=True, string='Name')

ShipmentReference()