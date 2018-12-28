from odoo import models, fields, api
# stock.pack.operation.lot

class PackOperationLot(models.Model):
    _inherit = "stock.pack.operation.lot"
    _order = 'date desc'

    product_id = fields.Many2one('product.product',string='Product',related='operation_id.product_id',readonly=True)
    product_uom = fields.Many2one('product.uom',string='Unit',related='operation_id.product_uom_id',readonly=True)
    date = fields.Datetime(string='Date', related='operation_id.date',readonly=True)
    imei_number = fields.Char(string='IMEI',related='lot_id.imei_number',readonly=True)
    location_id = fields.Many2one(string='Source Location',related='operation_id.location_id',readonly=True)
    location_dest_id = fields.Many2one(string='Destination Location', related='operation_id.location_dest_id', readonly=True)
