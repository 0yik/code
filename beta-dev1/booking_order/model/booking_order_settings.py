from odoo import fields,models,api,_

class BookingConfigSettings(models.Model):
    _name ="booking.order.settings"
    
    pre_booking = fields.Integer(string="Pre Booking time",required=True)
    post_booking = fields.Integer(String="Post Booking time",required=True)