# -*- coding: utf-8 -*-

from odoo import models, fields, api

class purchase_order_line(models.Model):
    _inherit = 'purchase.order.line'

    cost_element_id = fields.Many2one('project.cost_element', string="Cost Element")


