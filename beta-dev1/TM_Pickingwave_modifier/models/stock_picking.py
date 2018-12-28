# -*- coding: utf-8 -*-
# Copyright 2016 Serpent Consulting Services Pvt. Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class StockPickingWave(models.Model):
    _inherit = 'stock.picking.wave'

    vehicle_id = fields.Many2one('fleet.vehicle', 'Vehicle Number')



