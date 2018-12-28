# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PosDeliveryTimeframe(models.TransientModel):
    _inherit = 'pos.config.settings'

    time_frame_management  = fields.Boolean('Timeframe Management', implied_group="pos_delivery_timeframe_management.time_from_management_group")

    @api.multi
    def set_time_frame_management(self):
        ir_model = self.env['ir.model.data']
        group_user = ir_model.get_object('base', 'group_user')
        group_product = ir_model.get_object('pos_delivery_timeframe_management', 'time_from_management_group')
        if self.time_frame_management:
            group_user.write({'implied_ids': [(4, group_product.id)]})
        else:
            group_user.write({'implied_ids': [(3, group_product.id)]})
        return True

    def get_default_config_data(self, fields):
        config_data = self.search([])
        if config_data:
            return {
                'time_frame_management': config_data[-1].time_frame_management
            } 
        return {}

class PosConfig(models.Model):
    _inherit = 'pos.config'

    delivery_timeframe = fields.Boolean()