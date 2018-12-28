# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _

class res_branch(models.Model):
    _inherit = 'res.branch'

    delivery_charge_id = fields.Many2one('order.charge', string="Delivery Charge")