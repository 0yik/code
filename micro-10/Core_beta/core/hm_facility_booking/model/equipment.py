# -*- coding: utf-8 -*-

from odoo import api, fields, models

class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    required_booking = fields.Boolean("Requires Booking")

MaintenanceEquipment()