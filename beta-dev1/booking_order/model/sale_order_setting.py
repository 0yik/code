from odoo import api, fields, models,_

class SaleConfigSettings(models.TransientModel):
    _inherit = 'sale.config.settings'


    @api.model
    def get_pre_booking(self):
        pre_booking = self.env['booking.order.settings'].search([])
        if pre_booking:
            return pre_booking[0].pre_booking
        else:
            return 0
    
    @api.model
    def get_post_booking(self):
        post_booking = self.env['booking.order.settings'].search([])
        if post_booking:
            return post_booking[0].post_booking
        else:
            return 0
    
    pre_booking = fields.Integer(string='Pre Booking',default=get_pre_booking)
    post_booking = fields.Integer(string='Post Booking',default=get_post_booking)
    
    @api.multi
    def execute(self):
        booking_Config_setting_obj=self.env['booking.order.settings']
        if not booking_Config_setting_obj.pre_booking or not booking_Config_setting_obj.post_booking:
            booking_Config_setting_obj.create({'pre_booking':self.pre_booking,'post_booking':self.post_booking })
        else:
            booking_Config_setting_obj[0].pre_booking = self.pre_booking
            booking_Config_setting_obj[0].post_booking = self.post_booking
        return super(SaleConfigSettings,self).execute()
        
