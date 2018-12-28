# -*- coding: utf-8 -*-

from odoo import api, fields, models

class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    name = fields.Char('Facilty Name',required=True)
    location_id = fields.Many2one('location',string='Location')

MaintenanceEquipment()