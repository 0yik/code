# -*- coding: utf-8 -*-

from odoo import models,fields,api
from datetime import datetime
from odoo.exceptions import ValidationError
from __builtin__ import True

class stock_picking(models.Model):
    _inherit = 'stock.picking'
    
    is_booking = fields.Boolean("Is A Booking",default=False)
    start_date_actual = fields.Datetime("Actual Start Date")
    start_date_schedule = fields.Datetime("Schedule Start Date")
    end_date_actual = fields.Datetime("Actual End Date")
    end_date_schedule = fields.Datetime("Schedule End Date")
    booking_team_id = fields.Many2one("booking.team",'Team')
    leader_id = fields.Many2one("hr.employee","Team leader")
    employee_ids = fields.One2many("sale.employees","picking_id","Employees")
    equipments_ids = fields.One2many("team.equipmemnts","picking_id","Equipments")
    
    
 