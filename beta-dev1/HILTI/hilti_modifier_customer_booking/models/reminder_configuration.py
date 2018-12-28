# -*- coding: utf-8 -*-

from odoo import models, fields, api
import datetime

class admin_configuration(models.Model):
    _name = 'admin.configuration'
    _rec_name = "total_reminder"
    
    total_reminder = fields.Integer('Total Reminder')
    reminder_duration = fields.Integer('Reminder Duration')
    delay_time = fields.Integer('Delay Time')
    customer_booking_days = fields.Integer('Penalty days')
    
    
