# -*- coding: utf-8 -*-

from odoo import api, fields, models

class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    location_id = fields.Many2one('location',string='Location')

MaintenanceRequest()