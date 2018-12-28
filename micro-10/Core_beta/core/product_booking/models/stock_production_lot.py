from odoo import api, fields, models, _

class ProductSerialNumber(models.Model):
    _name = 'product.serial.number'
    _rec_name = 'product_id'

    booking_order_id = fields.Many2one('booking.order', 'Booking Order')
    booking_line_id = fields.Many2one('booking.order.line','Booking Order Line')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    serial_no = fields.Char(related='product_id.serial_no', string='Serial No', required=True)
    actual_start_date = fields.Date(string='Actual Start Date', required=True)
    actual_end_date = fields.Date(string='Actual End Date', required=True)