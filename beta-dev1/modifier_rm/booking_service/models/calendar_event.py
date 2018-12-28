# -*- coding: utf-8 -*-

from odoo import models,fields

class calendar_event(models.Model):
    _inherit = 'calendar.event'
    
    serial_number_ids = fields.Many2many('stock.production.lot','stock_production_lot_calendar_event_rel','event_id','serial_id',"Equipments")
    
    